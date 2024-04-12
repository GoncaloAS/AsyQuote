from wagtail.models import Orderable, Page
from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.snippets.models import register_snippet


@register_snippet
class Supplier(models.Model):
    name_supplier = models.CharField(max_length=255)

    def __str__(self):
        return self.name_supplier


@register_snippet
class Category(models.Model):
    name_category = models.CharField(max_length=255)

    def __str__(self):
        return self.name_category


class Products(Orderable):
    page = ParentalKey("ProductsPage", related_name="products", blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image'
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    price = models.CharField(blank=True, null=True)
    discounts = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    suppliers = ParentalManyToManyField(Supplier)
    categories = ParentalManyToManyField(Category)

    def __str__(self):
        return f"{self.title}"


class ProductsPage(RoutablePageMixin, Page):
    max_count = 1

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("products", label="products")],
            heading="Products",
        ),
    ]
