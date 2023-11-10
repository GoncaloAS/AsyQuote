from django.db import models
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm
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
    href_url = models.URLField(max_length=255, blank=True, null=True)


class FooterNavigation(Orderable):
    page = ParentalKey("Homepage", related_name="footer_navigation")
    navigation_text = models.CharField(max_length=255, blank=True, null=True)
    navigation_text_page = models.ForeignKey('wagtailcore.Page', null=True, blank=True, related_name='+',
                                             on_delete=models.SET_NULL)
    navigation_text_url = models.CharField(max_length=255, blank=True, null=True)


class FooterContact(Orderable):
    page = ParentalKey("Homepage", related_name="footer_contact")
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


class AdditionalInformation(Orderable):
    page = ParentalKey("Homepage", related_name="additional_information")
    additional_information_text = models.CharField(max_length=255, blank=True, null=True)
    additional_information_page = models.ForeignKey('wagtailcore.Page', null=True, blank=True, related_name='+',
                                                    on_delete=models.SET_NULL)


class Homepage(Page):
    max_count = 1
    template = "components/homepage/homepage.html"

    # logo
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

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

    # footer
    footer_navigation_title = models.CharField(max_length=255, null=True, blank=True)
    footer_contact_title = models.CharField(max_length=255, null=True, blank=True)
    copyright = models.CharField(max_length=255, null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('logo'),
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
        FieldPanel('footer_navigation_title'),
        MultiFieldPanel(
            [InlinePanel("footer_navigation", label="Navigation")],
            heading="Navigation",
        ),
        FieldPanel('footer_contact_title'),
        MultiFieldPanel(
            [InlinePanel("footer_contact", label="Contact")],
            heading="Contact",
        ),
        FieldPanel('copyright'),
        MultiFieldPanel(
            [InlinePanel("additional_information", label="Additional Information")],
            heading="Additional Information",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        return context
