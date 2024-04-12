from django.contrib import admin

from .models import Project, ServicesQuote, SectionQuote, PricesQuote, Notes

admin.site.register(Project)

admin.site.register(SectionQuote)
admin.site.register(ServicesQuote)
admin.site.register(PricesQuote)
admin.site.register(Notes)
