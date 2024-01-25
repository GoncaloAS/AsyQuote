from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image
from wagtail.models import Page, Orderable
from wagtail.snippets.models import register_snippet
from wagtailcaptcha.models import WagtailCaptchaEmailForm





@register_snippet
class CustomImage(Orderable):
    images_cards = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image'
    )

    def __str__(self):
        return self.images_cards.title if self.images_cards else 'CustomImage'


@register_snippet
class AdditionalInformation(models.Model):
    additional_information_text = models.CharField(max_length=255, blank=True, null=True)
    additional_information_href = models.CharField(max_length=255, blank=True, null=True)


@register_snippet
class WebsitePages(models.Model):
    text_pages = models.CharField(max_length=255, blank=True, null=True)
    pages_href = models.CharField(max_length=255, blank=True, null=True)


@register_snippet
class FooterContact(models.Model):
    information_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image'
    )
    information = models.CharField(max_length=255, blank=True, null=True)
    information_url = models.CharField(max_length=255, blank=True, null=True)


@register_snippet
class FooterTitles(models.Model):
    footer_navigation_title = models.CharField(max_length=255, null=True, blank=True)
    footer_contact_title = models.CharField(max_length=255, null=True, blank=True)
    copyright = models.CharField(max_length=255, null=True, blank=True)


class ImagesUses(blocks.StructBlock):
    image_uses = ImageChooserBlock(required=False, help_text="Select an image for each enterprise")
    url_uses = blocks.CharBlock(max_length=255, required=False, label='Url Imagem')


class ReviewHome(Orderable):
    page = ParentalKey("Homepage", related_name="review_home")
    review_card = models.ForeignKey(
        'CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='review_homes'
    )
    title_card = models.CharField(max_length=255, blank=True, null=True)
    paragraph_card = models.CharField(max_length=500, blank=True, null=True)
    letters_circle_card = models.CharField(max_length=3, blank=True, null=True)
    name_of_the_person_card = models.CharField(max_length=255, blank=True, null=True)
    function_of_the_person_card = models.CharField(max_length=255, blank=True, null=True)


class Faqs(Orderable):
    page = ParentalKey("Homepage", related_name="faqs")
    question = models.CharField(max_length=255, blank=True, null=True)
    answer = models.CharField(max_length=500, blank=True, null=True)
    text_href = models.CharField(max_length=255, blank=True, null=True)
    href_url = models.CharField(max_length=255, blank=True, null=True)


class Homepage(RoutablePageMixin, Page):
    max_count = 1

    @path('')
    def current_events(self, request):
        return self.render(
            request,
            template="components/homepage/homepage.html",
        )

    @path('termos-uso/')
    def current_events2(self, request):
        return self.render(
            request,
            template="components/redirects/termos.html",
        )

    @path('politica-privacidade/')
    def current_events3(self, request):
        return self.render(
            request,
            template="components/redirects/politica.html",
        )

    @path('creditos/')
    def current_event4(self, request):
        return self.render(
            request,
            template="components/redirects/creditos.html",
        )

    # @path('login/')
    # def current_event5(self, request):
    #     return self.render(
    #         request,
    #         template="account/login.html",
    #     )

    # hero section
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    hero_title = models.CharField(max_length=255, null=True, blank=True)
    hero_paragraph = RichTextField(max_length=255, null=True, blank=True)

    # uses section
    uses_title = models.CharField(max_length=255, null=True, blank=True)
    uses_image = StreamField([
        ('image', ImagesUses(label='Image')),
    ], blank=True, use_json_field=True)

    # about section
    about_title_1 = models.CharField(max_length=255, null=True, blank=True)
    about_paragraph_1 = models.CharField(max_length=255, null=True, blank=True)
    about_image_1 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    about_title_2 = models.CharField(max_length=255, null=True, blank=True)
    about_paragraph_2 = models.CharField(max_length=255, null=True, blank=True)
    about_image_2 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    about_title_3 = models.CharField(max_length=255, null=True, blank=True)
    about_paragraph_3 = models.CharField(max_length=255, null=True, blank=True)
    about_image_3 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # review section
    review_title = models.CharField(max_length=255, null=True, blank=True)

    # faqs
    faqs_title = models.CharField(max_length=255, null=True, blank=True)

    # action section
    action_title = models.CharField(max_length=255, null=True, blank=True)
    action_benefit = models.CharField(max_length=255, null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('hero_image'),
        FieldPanel('hero_title'),
        FieldPanel('hero_paragraph'),
        FieldPanel('uses_title'),
        FieldPanel('uses_image'),
        FieldPanel('about_title_1'),
        FieldPanel('about_paragraph_1'),
        FieldPanel('about_image_1'),
        FieldPanel('about_title_2'),
        FieldPanel('about_paragraph_2'),
        FieldPanel('about_image_2'),
        FieldPanel('about_title_3'),
        FieldPanel('about_paragraph_3'),
        FieldPanel('about_image_3'),
        FieldPanel('review_title'),
        MultiFieldPanel(
            [InlinePanel("review_home", label="Reviews")],
            heading="Reviews",
        ),
        FieldPanel('faqs_title'),
        MultiFieldPanel(
            [InlinePanel("faqs", label="FAQS")],
            heading="FAQS",
        ),
        FieldPanel('action_title'),
        FieldPanel('action_benefit'),

    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        return context
