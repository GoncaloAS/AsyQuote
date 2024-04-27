from django.contrib import admin

from .models import Products, Links, Supplier, Category

admin.site.register(Products)
admin.site.register(Links)
admin.site.register(Category)
admin.site.register(Supplier)
