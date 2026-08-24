from django.contrib import admin

from .models import Category, Links, Products, Supplier

admin.site.register(Products)
admin.site.register(Links)
admin.site.register(Category)
admin.site.register(Supplier)
