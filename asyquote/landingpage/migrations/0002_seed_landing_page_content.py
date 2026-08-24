"""Create the public landing page.

The institutional page is stored entirely in the database: its copy lives on the
Homepage model and its footer and navigation come from Wagtail snippets and a
wagtailmenus menu. That means a fresh clone that only runs `migrate` gets a site
with no public face at all, so this migration builds it.

Content is transcribed from the institutional page in the project report. The
artwork it references is committed under MEDIA_ROOT.

This imports the concrete models rather than using `apps.get_model`, because
building a Wagtail page needs the real treebeard methods and StreamField
handling. The trade-off is that a future schema change to these models can break
this migration on a fresh database.
"""
from django.db import migrations

IMAGES = [
    ("hero", "Construction-Illustration.jpg", "Obra em construção"),
    ("productivity", "Multitasking-bro_1.png", "Aumente a sua produtividade"),
    ("precision", "6491986_1.png", "Precisão e consistência"),
    ("data", "data_1.png", "Acesso rápido a dados cruciais"),
    ("client_logo", "obrascompinta-removebg-preview.png", "Obras com Pinta"),
    ("stars", "Component_22.png", "Cinco estrelas"),
    ("mail", "image_1.png", "Email"),
    ("phone", "image_2.png", "Telefone"),
]

REVIEWS = [
    ("O AsyQuote mudou a minha vida",
     "Estou impressionado com a eficiência desta ferramenta. Desde que comecei a usá-la, a "
     "minha empresa viu um aumento notável na produtividade e na precisão dos nossos "
     "orçamentos. A plataforma é incrivelmente intuitiva e economizou horas de trabalho "
     "manual. Além disso, o suporte ao cliente é excepcional. Definitivamente, uma escolha "
     "inteligente para qualquer empresa de construção!",
     "GS", "Gonçalo S.", "Estagiário"),
    ("Uma Revolução na Orçamentação",
     "O AsyQuote provou ser uma verdadeira revolução para o nosso processo de orçamentação. "
     "Desde a implementação, a nossa eficiência disparou, proporcionando uma melhoria "
     "significativa na precisão e rapidez na criação de orçamentos. A interface intuitiva "
     "facilitou a transição, e o suporte ao cliente atencioso solidificou nossa confiança na "
     "ferramenta. Recomendo a todas as empresas que buscam aprimorar sua abordagem orçamental.",
     "SO", "Sofia O.", "Diretora Financeira"),
    ("Eficiência Elevada com AsyQuote",
     "Testar o AsyQuote foi uma jogada estratégica para a nossa empresa. A eficiência que "
     "ganhamos desde então é notável. Os processos de orçamentação tornaram-se mais ágeis, "
     "economizando tempo valioso. A plataforma é amigável, e o suporte ao cliente, exemplar. "
     "Como gestor, essa ferramenta se tornou um aliado indispensável no dia a dia.",
     "PS", "Pedro S.", "Gerente de Projetos"),
]

FAQS = [
    ("Como posso criar um orçamento?",
     "Pode criar um orçamento através do nosso criador de orçamentos. Neste, poderá definir "
     "o produto, quantidades, margens de lucro e até descontos no produto.", "", ""),
    ("Como posso participar na fase beta",
     "Para participar na fase beta, tem que se inscrever no processo de seleção. Embora as "
     "vagas sejam limitadas, encorajamos todos a se candidatarem, pois valorizamos a "
     "contribuição de todos.", "Entre já na fase Beta", "aceder-beta"),
    ("Qual é preço da ferramenta?",
     "Como o AsyQuote encontra-se ainda em fase beta, decidimos que a melhor maneira de "
     "atrair mais usuários e melhorar a ferramenta, é deixar a ferramenta grátis para todos.",
     "", ""),
    ("O orçamento é costumizável?",
     "Sim o orçamento é costumizável, pode mudar o logo, os preços, as margens. Além disso, "
     "no final tem uma secção de notas aonde pode escrever o que quiser.", "", ""),
]

# The logo slider shows seven at a time and only autoplays when there are more
# slides than that, which is also what "10+ empresas" implies.
CLIENT_LOGO_COUNT = 10


def create_landing_page(apps, schema_editor):
    from pathlib import Path

    from django.conf import settings
    from PIL import Image as PILImage
    from wagtail.images.models import Image as WagtailImage
    from wagtail.models import Page
    from wagtail.models import Site as WagtailSite
    from wagtailmenus.models import MainMenu, MainMenuItem

    from asyquote.landingpage.models import (
        AdditionalInformation,
        CustomImage,
        Faqs,
        FooterContact,
        FooterTitles,
        Homepage,
        ReviewHome,
        WebsitePages,
    )

    if Homepage.objects.exists():
        return

    media = Path(settings.MEDIA_ROOT) / "original_images"

    def register(filename, title):
        """Point a Wagtail image at a file already present under MEDIA_ROOT."""
        path = media / filename
        if not path.exists():
            return None
        with PILImage.open(path) as probe:
            width, height = probe.size
        return WagtailImage.objects.create(
            title=title,
            file=f"original_images/{filename}",
            width=width,
            height=height,
        )

    img = {key: register(filename, title) for key, filename, title in IMAGES}

    # Wagtail's default welcome page already owns the 'home' slug, and the Site
    # points at it, so free the slug first and delete it once the Site has moved.
    for stale in Page.objects.filter(depth=2):
        stale.slug = f"wagtail-default-{stale.pk}"
        stale.save()

    root = Page.objects.get(depth=1)
    home = Homepage(
        title="AsyQuote",
        slug="home",
        hero_image=img["hero"],
        hero_title="Agilize os seus orçamentos",
        hero_paragraph="<p>Descubra como podemos otimizar o processo de orçamentação "
                       "para o seu negócio de construção.</p>",
        uses_title="10+ empresas usam o AsyQuote",
        about_title_1="Aumente a sua produtividade",
        about_paragraph_1="O AsyQuote pode produzir mais orçamentos em menos tempo, permitindo "
                          "que a sua empresa se concentre em projetos reais em vez de tarefas "
                          "administrativas. Maximize a produtividade e veja o seu negócio crescer.",
        about_image_1=img["productivity"],
        about_title_2="Precisão e consistência",
        about_paragraph_2="Garanta a precisão e consistência em todos os seus orçamentos. O "
                          "AsyQuote elimina erros humanos e padroniza o processo de orçamentação, "
                          "garantindo que cada orçamento atenda aos mais altos padrões de qualidade.",
        about_image_2=img["precision"],
        about_title_3="Acesso rápido a dados cruciais",
        about_paragraph_3="Tenha acesso instantâneo a dados de custos, materiais e mão de obra. "
                          "Com o AsyQuote, você pode tomar decisões informadas em tempo real, "
                          "adaptando-se às mudanças do mercado.",
        about_image_3=img["data"],
        review_title="Descubra o porquê dos nossos clientes gostarem de nós",
        faqs_title="Perguntas frequentes",
        action_title="Comece a usar o AsyQuote hoje",
        action_benefit="É grátis",
    )
    if img["client_logo"]:
        home.uses_image = [
            ("image", {"image_uses": img["client_logo"], "url_uses": "#"})
            for _ in range(CLIENT_LOGO_COUNT)
        ]
    root.add_child(instance=home)

    site, _ = WagtailSite.objects.get_or_create(
        is_default_site=True,
        defaults={"hostname": "localhost", "port": 8000, "root_page": home},
    )
    site.root_page = home
    site.site_name = "AsyQuote"
    site.save()

    for stale in Page.objects.filter(depth=2).exclude(pk=home.pk):
        stale.delete()

    # Review cards render review.review_card.images_cards.
    stars_card = CustomImage.objects.create(images_cards=img["stars"])
    for order, (title, para, letters, name, role) in enumerate(REVIEWS, start=1):
        ReviewHome.objects.create(
            page=home, sort_order=order, review_card=stars_card, title_card=title,
            paragraph_card=para, letters_circle_card=letters,
            name_of_the_person_card=name, function_of_the_person_card=role,
        )
    for order, (question, answer, text_href, href_url) in enumerate(FAQS, start=1):
        Faqs.objects.create(page=home, sort_order=order, question=question, answer=answer,
                            text_href=text_href, href_url=href_url)
    home.save_revision().publish()

    FooterTitles.objects.create(
        footer_navigation_title="Links Úteis",
        footer_contact_title="Contacte-nos",
        copyright="© 2023 AsyQuote - Todos os direitos Reservados",
    )
    # footer.html renders {% url nav.pages_href %}: a URL name, not a path. An
    # empty value falls through to the template's relative-link branch.
    for text, url_name in [("Login", "login"), ("Aceder Beta", "aceder-beta"), ("Homepage", "")]:
        WebsitePages.objects.create(text_pages=text, pages_href=url_name)

    FooterContact.objects.create(information="geral@asyquote.example",
                                 information_url="mailto:geral@asyquote.example",
                                 information_image=img["mail"])
    FooterContact.objects.create(information="+351 200 000 000",
                                 information_url="tel:+351200000000",
                                 information_image=img["phone"])

    # footer.html renders href="../{{ additional_information_href }}".
    for text, href in [("Política de privacidade", "politica-privacidade/"),
                       ("Créditos", "creditos/"),
                       ("Termos de uso", "termos-uso/")]:
        AdditionalInformation.objects.create(additional_information_text=text,
                                             additional_information_href=href)

    # The navbar renders {% main_menu %}; without items it shows only the logo.
    menu = MainMenu.get_for_site(site)
    for order, (text, url) in enumerate(
        [("Sobre", "#sobre"), ("Opiniões", "#opiniões"), ("FAQS", "#faqs"), ("Login", "login")],
        start=1,
    ):
        MainMenuItem.objects.create(menu=menu, sort_order=order, link_text=text, link_url=url)


def remove_landing_page(apps, schema_editor):
    from wagtail.images.models import Image as WagtailImage

    from asyquote.landingpage.models import (
        AdditionalInformation,
        CustomImage,
        FooterContact,
        FooterTitles,
        Homepage,
        WebsitePages,
    )

    titles = [title for _, _, title in IMAGES]
    Homepage.objects.all().delete()
    CustomImage.objects.all().delete()
    FooterTitles.objects.all().delete()
    FooterContact.objects.all().delete()
    WebsitePages.objects.all().delete()
    AdditionalInformation.objects.all().delete()
    WagtailImage.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):
    # Building the page writes to the search index and removing Wagtail's default
    # welcome page cascades into forms and redirects, so this has to run after
    # every Wagtail app has created its tables.
    dependencies = [
        ("landingpage", "0001_initial"),
        ("taggit", "0005_auto_20220424_2025"),
        ("wagtailadmin", "0003_admin_managed"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("wagtaildocs", "0012_uploadeddocument"),
        ("wagtailembeds", "0009_embed_cache_until"),
        ("wagtailforms", "0005_alter_formsubmission_form_data"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("wagtailmenus", "0023_remove_use_specific"),
        ("wagtailredirects", "0008_add_verbose_name_plural"),
        ("wagtailsearch", "0007_delete_editorspick"),
        ("wagtailusers", "0012_userprofile_theme"),
    ]

    operations = [
        migrations.RunPython(create_landing_page, remove_landing_page),
    ]
