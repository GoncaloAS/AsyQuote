from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from .forms import ProductsForm, CategoryForm, SupplierForm
from .models import (Products, Supplier, Category, Links)
from django.http import JsonResponse


class NotFoundProductView(TemplateView):
    template_name = '404/404_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductsPageView(TemplateView):
    template_name = 'products/products_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_suppliers = Supplier.objects.all()
        all_categorys = Category.objects.all()
        products = Products.objects.all()
        form = ProductsForm()
        form_categories = CategoryForm()
        form_supplier = SupplierForm()
        context['all_suppliers'] = all_suppliers
        context['all_categorys'] = all_categorys
        context['products'] = products
        context['form'] = form
        context['form_categories'] = form_categories
        context['form_supplier'] = form_supplier
        return context


def filter_products(request):
    category_names = request.GET.getlist('name_category', [])
    supplier_names = request.GET.getlist('name_supplier', [])
    search_query = request.GET.get('searchInput')

    products = Products.objects.all()
    user = request.user
    editor = False
    if category_names:
        category_filters = Q()
        for category_name in category_names:
            category_filters |= Q(categories__pk__in=category_name)
        products = products.filter(category_filters).distinct().order_by('-id')

    if supplier_names:
        supplier_filters = Q()
        for supplier_name in supplier_names:
            supplier_filters |= Q(suppliers__pk__in=supplier_name)
        products = products.filter(supplier_filters).distinct().order_by('-id')
        print(products)

    if search_query:
        products = products.filter(title__icontains=search_query).order_by('-id')

    if not (search_query or supplier_names or category_names):
        products = products.all()

    products_page_partial_html = render_to_string('products/products_page_partial.html',
                                                  {'products': products, 'user': user})
    return HttpResponse(products_page_partial_html)


def create_product(request):
    if request.method == 'POST':
        form = ProductsForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            uploaded_image = request.FILES.get('image')
            if uploaded_image:
                product.image = uploaded_image

            # Save the product first
            product.save()

            # Get the selected suppliers and their URLs and prices
            selected_suppliers = form.cleaned_data.get('suppliers')
            supplier_links = {}
            for supplier in selected_suppliers:
                supplier_link_key = f'supplierLink_{supplier.id}'
                supplier_price_key = f'supplierPrice_{supplier.id}'
                supplier_link_value = request.POST.get(supplier_link_key)
                supplier_price_value = request.POST.get(supplier_price_key)
                if supplier_link_value:
                    supplier_links[supplier] = (supplier_link_value, supplier_price_value)

            # Associate suppliers, URLs, and prices with the product
            for supplier, (link, price) in supplier_links.items():
                links_instance = Links.objects.create(url=link, supplier=supplier, price=price)
                product.links.add(links_instance)
                product.suppliers.add(supplier)

            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('products_page')
        else:
            messages.error(request, 'Erro ao criar produto. Verifique se as informações estão corretas.')
            return redirect('products_page')
    else:
        form = ProductsForm()

    return render(request, 'products/products_page.html', {'form': form})


def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            messages.success(request, 'Categoria adicionada com sucesso!')
            return redirect('products_page')
        else:
            messages.error(request, 'Erro ao criar Categoria. Verifique se as informações estão corretas.')
            return redirect('products_page')
    else:
        form = CategoryForm()

    return render(request, 'products/products_page.html', {'form_categories': form})


def create_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = form.save(commit=False)
            uploaded_image = request.FILES.get('image')
            if uploaded_image:
                supplier.image_supplier = uploaded_image
            supplier.save()
            messages.success(request, 'Fornecedor adicionado com sucesso!')
            return redirect('products_page')
        else:
            messages.error(request, 'Erro ao criar Fornecedor. Verifique se as informações estão corretas.')
            return redirect('products_page')
    else:
        form = CategoryForm()

    return render(request, 'products/products_page.html', {'form_supplier': form})


def update_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        updated_supplier_name = request.POST.get('update_supplier_name')
        updated_supplier_image = request.FILES.get('update_supplier_image')
        if updated_supplier_image:
            supplier.image_supplier = updated_supplier_image
        supplier.name_supplier = updated_supplier_name
        supplier.save()
        return JsonResponse({'success': 'Informações atualizadas com sucesso'})
    else:
        return JsonResponse({'error': 'Volte a preencher os campos.'})


def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        updated_category_name = request.POST.get('update_category_name')
        category.name_category = updated_category_name
        category.save()
        return JsonResponse({'success': 'Informações atualizadas com sucesso'})
    else:
        return JsonResponse({'error': 'Volte a preencher os campos.'})


def update_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.method == 'POST':
        print("ola")
