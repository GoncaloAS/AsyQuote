from django.conf import settings
from wagtail.models import Orderable, Page
from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from modelcluster.fields import ParentalKey
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from django.shortcuts import render


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
    URL = models.URLField(blank=True, null=True)
    supplier = models.CharField(blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)


# class UserProductConfig(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     product = models.ForeignKey(Products, on_delete=models.CASCADE)
#     discount = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True, default=0)
#
#     def __str__(self):
#         return f"{self.user.username} - {self.product.title}"


class ProductsPage(RoutablePageMixin, Page):
    @path('builder/produtos/')
    def builder_produtos(self, request):
        return self.render(
            request,
            template="builder/builder_produtos.html",
        )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("products", label="products")],
            heading="Products",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        return context
