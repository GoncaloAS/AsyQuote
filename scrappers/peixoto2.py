"""Scrape a supplier catalogue into the spreadsheets the products importer reads.

There is no supplier API, so this walks the storefront. Two passes: discover the
category URLs, then page through each category collecting title, product URL,
price and image URL. Output per category is a six-column .xlsx plus a folder of
images, which is exactly the shape `products.views.upload_excel` expects.

The crawl obeys robots.txt: rules are fetched at start-up, every URL is checked
before it is requested, and the site's Crawl-delay is honoured by default. The
user agent identifies the tool rather than impersonating a browser.

    python scrappers/peixoto2.py --list-categories
    python scrappers/peixoto2.py --categories 1 --max-pages 2
    python scrappers/peixoto2.py --yes

Run `--help` for the full set of limits.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scrappers import robots  # noqa: E402

SITE = "https://casapeixoto.pt"
CATALOGUE_URL = f"{SITE}/2-produtos"
SUPPLIER = "Casa Peixoto"
PAGE_SIZE_HINT = 24

# Identify the tool. Impersonating Chrome would mean the site cannot tell who is
# crawling it, or apply its own rules to us.
USER_AGENT = "AsyQuoteScraper/1.0 (+https://github.com/GoncaloAS/AsyQuote)"
DEFAULT_DELAY = 1.0
RETRY_LIMIT = 5


class Throttle:
    """Enforce a minimum interval between the start of successive requests."""

    def __init__(self, delay: float):
        self.delay = delay
        self._last = 0.0

    def wait(self) -> None:
        gap = self.delay - (time.monotonic() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()


class Crawler:
    """Fetch pages politely, skipping anything robots.txt disallows.

    Requests rather than aiohttp: the site sits behind Cloudflare, which
    fingerprints the client and answers aiohttp with 403 even for a URL its own
    robots.txt allows and with an identical User-Agent. Since the declared
    Crawl-delay serialises the crawl anyway, the async machinery bought nothing.
    """

    def __init__(self, rules: robots.Rules, throttle: Throttle, headers: dict):
        self.rules = rules
        self.throttle = throttle
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.skipped: list[str] = []

    def get(self, url: str) -> bytes | None:
        if not self.rules.allows(url):
            self.skipped.append(url)
            print(f"  robots.txt disallows, skipping: {url}")
            return None
        for attempt in range(RETRY_LIMIT):
            self.throttle.wait()
            try:
                response = self.session.get(url, timeout=60)
            except requests.RequestException as exc:
                backoff = 2**attempt
                print(f"  {type(exc).__name__} on {url}; retrying in {backoff}s")
                time.sleep(backoff)
                continue
            if response.status_code == 200:
                return response.content
            if response.status_code == 429 or response.status_code >= 500:
                backoff = 2**attempt
                print(f"  HTTP {response.status_code} on {url}; retrying in {backoff}s")
                time.sleep(backoff)
                continue
            print(f"  HTTP {response.status_code} for {url}")
            return None
        print(f"  giving up on {url} after {RETRY_LIMIT} attempts")
        return None


def discover_categories(rules: robots.Rules, headers: dict, start_at: str | None) -> list[str]:
    if not rules.allows(CATALOGUE_URL):
        sys.exit(f"robots.txt disallows {CATALOGUE_URL}; nothing to do.")
    response = requests.get(CATALOGUE_URL, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    urls: list[str] = []
    for menu in soup.find_all("ul", {"class": "category-sub-menu"}):
        for item in menu.find_all("li", {"data-depth": "0"}):
            link = item.find("a")
            if not link or not link.get("href"):
                continue
            url = urljoin(SITE, link["href"])
            if url not in urls:
                urls.append(url)

    if start_at:
        matches = [i for i, u in enumerate(urls) if start_at in u]
        if matches:
            urls = urls[matches[0] :]
        else:
            print(f"  --start-at {start_at!r} matched nothing; keeping all categories")
    return [u for u in urls if rules.allows(u)]


def parse_listing(html: bytes) -> tuple[list[str], list[str], list[str], list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    titles, hrefs, prices, images = [], [], [], []

    for block in soup.find_all(class_="product-image"):
        img = block.select_one("img")
        if img and img.get("src"):
            images.append(img["src"])
    for block in soup.find_all(class_="product-meta"):
        for anchor in block.select("a"):
            titles.append(anchor.get_text(strip=True))
            hrefs.append(anchor["href"])
    for block in soup.find_all(class_="price"):
        prices.append(block.get_text(strip=True))

    return titles, hrefs, prices, images


def scrape_category(crawler: Crawler, url: str, max_pages: int) -> dict[str, list[str]]:
    """Page through one category until a page comes back with no priced products."""
    rows: dict[str, list[str]] = {"Title": [], "Href": [], "Price": [], "imagem": []}
    for page in range(1, max_pages + 1):
        html = crawler.get(f"{url}?page={page}")
        if html is None:
            break
        titles, hrefs, prices, images = parse_listing(html)
        if not prices:
            break
        rows["Title"].extend(titles)
        rows["Href"].extend(hrefs)
        rows["Price"].extend(prices)
        rows["imagem"].extend(images)
        print(f"  page {page}: {len(prices)} products (running total {len(rows['Price'])})")
        if len(prices) < PAGE_SIZE_HINT:
            break
    return rows


def download_images(crawler: Crawler, folder: Path, urls: list[str]) -> int:
    folder.mkdir(parents=True, exist_ok=True)
    saved = 0
    for index, image_url in enumerate(urls):
        data = crawler.get(urljoin(SITE, image_url))
        if data is None:
            continue
        # Positional names: the importer zips rows and images by index.
        (folder / f"image_{index + 1}.jpg").write_bytes(data)
        saved += 1
    return saved


def write_sheet(rows: dict[str, list[str]], category: str, out_dir: Path) -> Path:
    count = min(len(rows["Title"]), len(rows["Href"]), len(rows["Price"]), len(rows["imagem"]))

    # Listings carry "Preço sob consulta" rows. upload_excel drops a price it
    # cannot parse but keeps the title, which shifts every later row against its
    # price and image and makes the whole import fail its length check. A product
    # with no price is useless in a price catalogue, so drop it here instead -
    # across all four columns at once, keeping them aligned.
    keep = [i for i in range(count) if re.search(r"\d", str(rows["Price"][i]))]
    dropped = count - len(keep)
    if dropped:
        print(f"  dropped {dropped} products with no numeric price")

    frame = pd.DataFrame(
        {
            "Title": [rows["Title"][i] for i in keep],
            "Href": [rows["Href"][i] for i in keep],
            "Price": [rows["Price"][i] for i in keep],
            "imagem": [rows["imagem"][i] for i in keep],
            "Category": [category] * len(keep),
            "Supplier": [SUPPLIER] * len(keep),
        }
    )
    path = out_dir / f"{category}_products.xlsx"
    frame.to_excel(path, sheet_name="products", index=False)
    print(f"  wrote {len(keep)} rows to {path}")
    return path


def run(args, rules: robots.Rules, headers: dict, categories: list[str]) -> None:
    delay = args.delay if args.delay is not None else (rules.crawl_delay or DEFAULT_DELAY)
    crawler = Crawler(rules, Throttle(delay), headers)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"Category": categories}).to_excel(
        out_dir / "products_links.xlsx", sheet_name="products_links", index=False
    )
    print(f"category map -> {out_dir / 'products_links.xlsx'}\n")

    for number, url in enumerate(categories, start=1):
        name = urlparse(url).path.strip("/").split("/")[-1]
        print(f"[{number}/{len(categories)}] {name}")
        rows = scrape_category(crawler, url, args.max_pages)
        if not rows["Price"]:
            print("  no products found\n")
            continue
        sheet = write_sheet(rows, name, out_dir)
        if args.images:
            folder = out_dir / sheet.stem
            saved = download_images(crawler, folder, rows["imagem"])
            print(f"  saved {saved} images to {folder}")
        print()

    if crawler.skipped:
        print(f"skipped {len(crawler.skipped)} URLs disallowed by robots.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--categories", type=int, default=0, help="only crawl the first N categories (0 = all)")
    parser.add_argument("--max-pages", type=int, default=200, help="page cap per category (default 200)")
    parser.add_argument("--delay", type=float, default=None, help="seconds between requests (default: robots.txt)")
    parser.add_argument("--out", default="scrappers/output", help="output directory")
    parser.add_argument("--start-at", default=None, help="skip categories until one matches this substring")
    parser.add_argument("--no-images", dest="images", action="store_false", help="spreadsheets only")
    parser.add_argument("--list-categories", action="store_true", help="print the category map and exit")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation for a long run")
    args = parser.parse_args()

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9",
    }
    cookie = os.environ.get("SCRAPER_COOKIE")
    if cookie:
        headers["Cookie"] = cookie

    print(f"fetching {SITE}/robots.txt as {USER_AGENT}")
    robots_txt = requests.get(f"{SITE}/robots.txt", headers=headers, timeout=30)
    rules = robots.parse(robots_txt.text if robots_txt.ok else "", USER_AGENT)
    print(f"  rules for {rules.matched_agent!r}: {len(rules.allow)} allow, {len(rules.disallow)} disallow")
    if rules.content_signal:
        print(f"  Content-Signal: {rules.content_signal}")
    print(f"  Crawl-delay: {rules.crawl_delay if rules.crawl_delay is not None else 'not set'}")

    categories = discover_categories(rules, headers, args.start_at)
    if args.categories:
        categories = categories[: args.categories]
    print(f"  {len(categories)} categories allowed\n")

    if args.list_categories:
        for url in categories:
            print(f"  {url}")
        return
    if not categories:
        sys.exit("nothing to crawl")

    delay = args.delay if args.delay is not None else (rules.crawl_delay or DEFAULT_DELAY)
    pages = len(categories) * min(args.max_pages, 40)
    estimate = pages * delay * (1 + (PAGE_SIZE_HINT if args.images else 0))
    print(f"at {delay}s per request this is roughly {estimate / 3600:.1f} h of crawling")
    if estimate > 600 and not args.yes:
        sys.exit("refusing to start a long crawl without --yes")

    run(args, rules, headers, categories)


if __name__ == "__main__":
    main()
