from wagtail.models import Orderable, Page
from django.db import models
import requests


class Supplier(models.Model):
    name_supplier = models.CharField(max_length=255)
    image_supplier = models.ImageField(upload_to='supplier_images/', verbose_name='supplier-image', null=True,
                                       blank=True)

    def __str__(self):
        return self.name_supplier


class Category(models.Model):
    name_category = models.CharField(max_length=255)

    def __str__(self):
        return self.name_category


class Links(models.Model):
    url = models.URLField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=7, default='')

    def __str__(self):
        return self.url


class Products(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='products_images/', verbose_name='Image-products', null=True, blank=True)
    title = models.CharField(max_length=255, default='')
    suppliers = models.ManyToManyField(Supplier)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, null=True)
    links = models.ManyToManyField(Links, blank=True)

    def minimum_price(self):
        prices = [link.price for link in self.links.all()]
        return min(prices, default=None)

    def minimum_price_info(self):
        prices_info = [(link.price, link.supplier.name_supplier, link.url) for link in self.links.all()]
        if prices_info:
            min_price_info = min(prices_info, key=lambda x: x[0])
            return min_price_info
        else:
            return (None, None, None)
