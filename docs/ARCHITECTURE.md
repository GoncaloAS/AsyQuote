# Architecture

Companion to the [README](../README.md). This describes how AsyQuote is put
together, and is candid about where the design does not hold up.

## Layout

Generated from `cookiecutter-django`, so `config/` holds settings and the root
urlconf while application code lives under `asyquote/`.

| Path | Responsibility |
|---|---|
| `config/settings/base.py` | Everything shared. Installed apps, Wagtail, allauth, Argon2 hashing, password validators, email, reCAPTCHA keys |
| `config/settings/local.py` | `DEBUG`, debug toolbar, django-extensions, console email, reCAPTCHA test-key check silenced |
| `config/settings/production.py` | Redis cache, HSTS/SSL, Mailgun via Anymail, Sentry. Every secret read from the environment |
| `config/urls.py` | One flat urlconf for the whole project — no per-app `urls.py` except `users/` |
| `asyquote/users/` | `User(AbstractUser)`, allauth adapters, signup form with captcha |
| `asyquote/clients/` | `Client`, owner-scoped list view, NIF validation |
| `asyquote/products/` | Catalogue models, listing/filtering, in-page backoffice, spreadsheet import |
| `asyquote/projects/` | `Project` and the quote tree, all builder endpoints, both Excel exports |
| `asyquote/landingpage/` | Wagtail `Homepage` plus the snippets the public site renders |
| `asyquote/utils/` | Context processors injecting footer/navigation snippets into every template |
| `settings_conta/` | Account settings page; subclasses allauth's password-reset and email views |
| `scrappers/` | Supplier catalogue scraper. A standalone script, not wired into Django |
| `compose/local/django/` | Dev image, entrypoint (waits on Postgres), start script (migrate + seed) |

`config/urls.py` being flat is why every view is imported at the top of it. It
works at this size and would not at three times this size.

## Data model

### The quote tree

```
Project ──1:1(by convention)── Notes
   │  key (UUID)
   │
   ├── SectionQuote   project_key, section_count,                      name, visible
   │      │
   │      ├── ServicesQuote  project_key, section_key, service_count,  name, quantity, visible
   │      │      │
   │      │      └── PricesQuote  project_key, section_key, services_key, prices_count,
   │      │                       description, cost, charged, profit_money, profit_percentage, visible
```

The indentation above is a convention, not a constraint. **There are no foreign
keys between these four models.** A child is associated with its parent by
carrying the project's `key` UUID plus the integer position of each ancestor:

- `SectionQuote` is identified by `(project_key, section_count)`
- `ServicesQuote` by `(project_key, section_key, service_count)`
- `PricesQuote` by `(project_key, section_key, services_key, prices_count)`

Consequences, all of which the code lives with:

- The database cannot reject a price line pointing at a service that does not exist
- Deleting a project does not cascade; `delete_project` deletes each table by hand
- Nothing is unique or indexed, so every read filters on three loose integers
- Two rows can share a position if two requests insert concurrently, because the
  next index comes from a `Max()` read in Python rather than a database sequence

Rows are hidden rather than removed. `delete_fields_quote` sets `visible = False`
on a row and its descendants, first checking a sibling remains, so a quote always
has at least one chapter, each chapter one service, each service one price line.
Positions are therefore never reused and grow monotonically.

Money is derived in two places:

- `PricesQuote.save` computes `profit_money = charged - cost` and stores the
  percentage. `profit_percentage` is a `CharField` holding `str(float)`, which is
  why the HTML table needs `|floatformat:2` to be readable.
- `Project.total_cost` / `total_charged` aggregate `Sum` over the project's
  `PricesQuote` rows; `profit_percentage()` derives the margin from those two,
  guarding division by zero.

`Project.save` allocates the `key` UUID in a retry loop and creates the project's
`Notes` row on first save.

### The catalogue

```
Supplier ──┐
           ├── Links (url, price, supplier FK)
Category   │        │
   │       │        │ M2M
   └── Products (title, image, categories FK, suppliers M2M, links M2M)
```

Conventional Django, and the sounder half of the schema. One `Links` row is one
supplier's URL and price for one product, so a product carries as many prices as
suppliers stock it. `Products.minimum_price_info` returns
`(price, supplier_name, url)` for the cheapest, which is what both the catalogue
listing and the builder's search display.

`Products.suppliers` is redundant — a product's suppliers are derivable from its
`links` — but it is maintained alongside, so the two can drift.

### Clients, users, content

`Client` has a `user` foreign key and a `nif` `CharField(max_length=9)`.
`total_charged_amount()` sums the charged value of every `PricesQuote` belonging
to the client's projects, so a client's worth follows their quotes.

`User` extends `AbstractUser` with two booleans, `receive_email` and
`development_help`. Authentication is by username; email is required and must be
verified.

`landingpage` is Wagtail. `Homepage` is a `RoutablePageMixin` page whose extra
routes (`termos-uso/`, `politica-privacidade/`, `creditos/`) render static
templates, with `ReviewHome` and `Faqs` as `Orderable` children edited inline.
The footer and navigation come from four registered snippets — `FooterTitles`,
`FooterContact`, `WebsitePages`, `AdditionalInformation` — injected into every
template by `asyquote/utils/context_processors.py`. The navbar is a
`wagtailmenus` `MainMenu`.

**All of that is content, not code**, which means a fresh database renders a
site with no public face: no hero, no navigation, no footer. The data migration
`landingpage/0002_seed_landing_page_content` therefore creates the page, its
imagery, the snippets and the menu, so `migrate` alone yields a working
institutional page. It imports the concrete models instead of using
`apps.get_model`, because building a Wagtail page needs the real treebeard and
StreamField behaviour; the cost is that a later schema change to these models
can break the migration on a fresh database. It also has to depend on the tip of
every Wagtail app, since publishing a page writes to the search index and
removing Wagtail's default welcome page cascades into forms and redirects.

One sharp edge worth knowing: the logo slider is slick with `slidesToShow: 7`,
and slick does not autoplay when the slide count does not exceed what is on
screen. The migration seeds ten client logos for that reason.

Note that `WebsitePages.pages_href` stores a **URL name**, not a path: the footer
renders it through `{% url nav.pages_href %}`, so a value like `/builder/products/`
raises `NoReverseMatch` and takes the whole page down. `AdditionalInformation`,
two fields away, stores a relative path instead. Same-looking fields, opposite
contracts, no validation on either.

## Request flow

### The builder

The builder page loads once and then talks to four GET endpoints, each of which
returns a re-rendered template partial as JSON:

| Endpoint | Purpose |
|---|---|
| `save_quote_url` | Structural inserts (`add-section`, `add-service`, `add-price`) |
| `save_quote_data` | Field edits — chapter name, service name, quantity, description, cost, charged, notes |
| `create_fields_quote` / `delete_fields_quote` | Insert-at-position and soft delete |
| `filter_edit_products` | Product search in the sidebar |

Each returns `{'form_html': ...}` from `render_to_string`, and the client swaps
it into the DOM. The server owns rendering; the JS moves HTML and manages focus.

This keeps the display and the database in step with no client-side model, at the
cost of a full partial re-render per keystroke-committed change, and of every one
of these being a **`GET` that writes** — outside CSRF protection.

The product search is the one query worth reading:

```python
min_price_subquery = Links.objects.filter(
    products__id=OuterRef('id')
).values('products__id').annotate(min_price=Min('price')).values('min_price')

filtered_products = products.filter(title__icontains=value).annotate(
    minimum_price=Subquery(min_price_subquery, output_field=DecimalField())
).order_by('minimum_price')
```

One query returns matches ordered cheapest-first, instead of loading each
product and calling `minimum_price()` per row.

### Excel export

Two exports, both `openpyxl`, both streamed straight into an `HttpResponse` with
a spreadsheet content type — nothing is written to disk.

`download_excel` is the flat one: a row per project with cost, charged, margin
and state, plus a totals row, with column widths measured from the longest value
in each column.

`download_project_quote` builds the proposal. It walks the visible chapters in
`section_count` order, then services, then price lines, tracking a `current_row`
cursor and two counters that produce the article numbering (`1`, `1.1`,
`1.1.1`). Per line it splits the free-text quantity into number and unit,
writes the unit price, and writes the line total as the **formula**
`=C{row}*E{row}` so the recipient can change a quantity and see the total update.
Chapter subtotals are filled green, the proposal total grey, and the whole grid
gets thin outer / dotted inner borders. `print_title_rows = '1:4'` repeats the
header block on every printed page.

### Scraper → catalogue

```
peixoto2.py                                      products/views.py
───────────                                      ─────────────────
category menu ─► products_links.xlsx
                        │
                        └─► per category:
                            gather(10 pages) ──► <category>_products.xlsx ──► upload_excel
                            gather(images)   ──► <category>_products/           │
                                                                                ├─ resolve/create Category
                                                                                ├─ require existing Supplier
                                                                                ├─ delete that (supplier, category)
                                                                                ├─ gather(image downloads)
                                                                                └─ create Products + Links
```

The handoff is a six-column sheet: title, product URL, price, image URL,
category, supplier.

`scrappers/robots.py` parses the site's rules on every run and every URL is
checked before it is fetched; `scrappers/peixoto2.py` throttles requests to the
declared `Crawl-delay`, identifies itself honestly, and takes `--categories`,
`--max-pages`, `--delay` and `--no-images` so a small run is easy. The matcher is
hand-written because `urllib.robotparser` gets wildcard `Disallow` patterns
wrong. On import, one `asyncio.gather` fetches every image URL in the sheet.

The import has the sharp edges: it deletes the existing products for a
supplier/category pair *before* the new rows are validated, inserts row by row
rather than with `bulk_create`, and wraps everything in one broad
`except Exception` that reports the error as a flash message.

## Settings and secrets

`base.py` reads every credential through `django-environ`:
`DJANGO_SECRET_KEY`, `DATABASE_URL`, the `EMAIL_*` block, `RECAPTCHA_*`,
`WAGTAILADMIN_BASE_URL`; production adds `REDIS_URL`, `SENTRY_DSN`,
`MAILGUN_*` and `DJANGO_ADMIN_URL`. `.env.example` is the full list.
`.env` is git-ignored.

Locally, reCAPTCHA falls back to Google's public test keys (which always
validate) and SMTP points at the mailpit container, so registration works end to
end with no third-party account: the confirmation mail is genuinely sent and
read back at http://localhost:8025.

`EMAIL_HOST` and the reCAPTCHA keys both use `env(...) or <fallback>` rather
than `env(..., default=...)`, because django-environ treats an empty variable as
set. `.env.example` leaves both blank on purpose, and an empty site key silently
broke signup once already. `local.py` silences
`captcha.recaptcha_test_key_error`, which is an error-level system check that
otherwise aborts every management command.

Security-relevant settings worth naming: Argon2 first in `PASSWORD_HASHERS`,
all four `AUTH_PASSWORD_VALIDATORS` on, `PASSWORD_RESET_TIMEOUT = 120`,
`ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, `ATOMIC_REQUESTS = True`,
`SESSION_COOKIE_HTTPONLY`, `CSRF_COOKIE_HTTPONLY`, `X_FRAME_OPTIONS = "DENY"`.

## Authorisation, and where it is missing

Every view scopes its own lookups to `request.user`; there is no owner-aware
manager doing it centrally. That discipline was originally applied unevenly, and
for a long time most of the endpoints that mutate a quote looked their object up
by `project_key` or by id alone — so an authenticated user who learned another
user's quote UUID or client id could read and edit it, and several of those
endpoints took no login at all.

They now all resolve through `owned_project(request, key)`, or a
`get_object_or_404(..., user=request.user)`, so a foreign object is a 404:

| Area | Enforced by |
|---|---|
| `project_list`, `ClientListView`, `filter_*` | `@login_required` + queryset filtered on the user |
| `edit_project`, `delete_project`, `download_project_quote` | `owned_project()` |
| `save_quote_data`, `save_quote_url`, `create_fields_quote`, `delete_fields_quote`, `filter_edit_products` | `owned_project()` on the `key` parameter |
| `update_project` | `get_object_or_404(Project, pk=..., user=request.user)` |
| `update_client`, `delete_client` | `get_object_or_404(Client, id=..., user=request.user)` |
| catalogue writes (`create_*`, `update_*`, `delete_*`, `upload_excel`) | `@superuser_required` — previously gated only by hiding the controls in the template |

`asyquote/projects/tests/test_permissions.py` covers each of these from the
point of view of a second, logged-in user.

What has *not* changed is the method: these are still `GET` requests that write,
so they sit outside CSRF protection. Moving the mutations to `POST` is the
remaining half of the job.

## Frontend

Django templates with Bootstrap 5, one Sass partial and one JS bundle per page
area, built by `gulpfile.js` into `static/css/project.min.css` and
`static/js/vendors.min.js`. The compiled output is committed, so the application
runs without a Node toolchain; `npm run build` is only needed to change styles.

Interactivity is jQuery AJAX against the endpoints above, with `iziToast` for the
flash messages that come back in JSON error responses. htmx is loaded too — but
from `unpkg.com` at request time rather than bundled, and only for a couple of
`htmx:afterSwap` hooks in the product modal, while the `django-htmx` package
listed in `requirements/base.txt` is never added to `INSTALLED_APPS`. Two
overlapping approaches to the same problem, one of which puts a third-party CDN
in the critical path of every page load.

## Testing

`pytest` with `pytest-django`, `--reuse-db`, settings `config.settings.test`.
59 tests:

| File | Covers |
|---|---|
| `projects/tests/test_margins.py` | per-line profit, quote totals, the zero-cost case, and that a soft-deleted line stops counting |
| `projects/tests/test_excel_export.py` | both exports: header block, repeated print titles, live `=C*E` formulas, article numbering, chapter subtotals, hidden lines left out, and that neither leaks another user's quotes |
| `projects/tests/test_permissions.py` | every mutating endpoint, from the point of view of a second logged-in user |
| `clients/tests/test_clients.py` | the NIF rules, per-owner uniqueness, and the guard against deleting a client that has quotes |
| `users/tests/` | the cookiecutter suite over the admin, the creation form and the user views |

`projects/tests/factories.py` builds a quote — chapter, service, two priced
lines — so a test reads as the arithmetic it is checking.

What is still untested is the quote tree's own operations: inserting a chapter,
soft-deleting a service, the positional bookkeeping in between. That is the part
of the design that is weakest, and pinning it down properly means changing the
schema first rather than freezing the current behaviour in tests.
