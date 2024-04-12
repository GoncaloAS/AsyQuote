from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from .models import (Products, ProductsPage, Supplier, Category,
    # CategoryProducts
                     )
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.contrib.auth.decorators import login_required


class NotFoundProductView(TemplateView):
    template_name = '404/404_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_suppliers = Supplier.objects.all()
        all_categorys = Category.objects.all()

        context['all_suppliers'] = all_suppliers
        context['all_categorys'] = all_categorys

        return context


class ProductsPageView(TemplateView):
    template_name = 'products/products_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_suppliers = Supplier.objects.all()
        all_categorys = Category.objects.all()
        products = Products.objects.all()
        context['all_suppliers'] = all_suppliers
        context['all_categorys'] = all_categorys
        context['products'] = products
        return context


def filter_products(request):
    category_names = request.GET.getlist('name_category', [])
    supplier_names = request.GET.getlist('name_supplier', [])
    search_query = request.GET.get('searchInput')
    products = Products.objects.all()

    if category_names:
        category_filters = Q()
        for category_name in category_names:
            category_filters |= Q(categoryproducts__category__pk=category_name)
        products = products.filter(category_filters)

    if supplier_names:
        supplier_filters = Q()
        for supplier_name in supplier_names:
            supplier_filters |= Q(supplierproducts__supplier__pk=supplier_name)
        products = products.filter(supplier_filters)

    if search_query:
        products = products.filter(title__icontains=search_query)
    html = render_to_string('products/products_list_partial.html', {'products': products})
    return HttpResponse(html)
