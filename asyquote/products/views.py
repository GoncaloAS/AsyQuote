import os
import re
import aiohttp
import asyncio
from decimal import Decimal, DecimalException
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.db import transaction
from .forms import ProductsForm, CategoryForm, SupplierForm, UploadExcelForm
from .models import (Products, Supplier, Category, Links)
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import ListView, UpdateView
from openpyxl import load_workbook
from django.core.files.base import ContentFile
import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.http import QueryDict


class NotFoundProductView(TemplateView):
    template_name = '404/404_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductsListView(ListView):
    template_name = 'products/products_page.html'
    model = Products
    paginate_by = 24
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_suppliers = Supplier.objects.all()
        all_categorys = Category.objects.all()
        form = ProductsForm()
        form_categories = CategoryForm()
        form_supplier = SupplierForm()
        form_excel = UploadExcelForm()
        context['all_suppliers'] = all_suppliers
        context['all_categorys'] = all_categorys
        context['form'] = form
        context['form_categories'] = form_categories
        context['form_supplier'] = form_supplier
        context['form_excel'] = form_excel
        return context

    def get_queryset(self):
        return Products.objects.all().order_by('-id')


def filter_products(request):
    category_names = request.GET.getlist('name_category', [])
    supplier_names = request.GET.getlist('name_supplier', [])
    search_query = request.GET.get('searchInput')

    products = Products.objects.all().order_by('-id')
    user = request.user
    editor = False

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)

    if category_names:
        category_filters = Q()
        for category_name in category_names:
            category_filters |= Q(categories__pk=category_name)
        products = products.filter(category_filters).order_by('-id')

    if supplier_names:
        supplier_filters = Q()
        for supplier_name in supplier_names:
            supplier_filters |= Q(suppliers__pk__in=supplier_name)
        products = products.filter(supplier_filters).distinct().order_by('-id')

    if search_query:
        products = products.filter(title__icontains=search_query).order_by('-id')

    if not (search_query or supplier_names or category_names):
        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

    products_page_partial_html = render_to_string('products/products_page_partial.html',
                                                  {'products': products, 'user': user})
    return HttpResponse(products_page_partial_html)


# region Section CRUD: Create
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


# endregion

# region Section CRUD: Update
def update_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        updated_supplier_name = request.POST.get('update_supplier_name')
        supplier_image_name = 'update_supplier_image' + str(supplier_id)
        supplier_image_url = request.POST.get('supplier_image_url')
        updated_supplier_image = request.FILES.get(supplier_image_name)
        if updated_supplier_image:
            supplier.image_supplier = updated_supplier_image
        supplier.name_supplier = updated_supplier_name
        supplier.save()
        messages.success(request, 'Fornecedor atualizado com sucesso!')
    else:
        messages.error(request, 'Erro ao atualizar fornecedor.')
    return redirect('products_page')


def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        updated_category_name = request.POST.get('update_category_name')
        category.name_category = updated_category_name
        category.save()
        messages.success(request, 'Categoria atualizada com sucesso!')
    else:
        messages.error(request, 'Erro ao atualizar categoria.')
    return redirect('products_page')


def update_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.method == 'POST':
        updated_product_title = request.POST.get('update_product_title')
        updated_product_image = request.FILES.get('update_product_image_' + str(product_id))
        product.title = updated_product_title
        if updated_product_image:
            product.image = updated_product_image
        category_id = request.POST.get('categories')
        category = Category.objects.get(id=category_id)
        product.categories = category
        product.save()
        supplier_ids = request.POST.getlist('suppliers')
        suppliers = Supplier.objects.filter(id__in=supplier_ids)
        product.suppliers.set(suppliers)
        product.links.clear()

        for supplier in suppliers:
            url = request.POST.get(f'supplierLink_{supplier.id}', '')
            price_str = request.POST.get(f'supplierPrice_{supplier.id}', '')
            if ',' in price_str:
                price_str = price_str.replace(',', '.')
            try:
                price_decimal = Decimal(price_str)
            except (ValueError, DecimalException):
                pass
            link = Links.objects.create(url=url, supplier=supplier, price=price_decimal)
            product.links.add(link)

        messages.success(request, 'Produto atualizado com sucesso!')
    else:
        messages.success(request, 'Erro ao atualizar produto.')
    return redirect('products_page')


# endregion

# region Section CURD: Delete
def delete_product(request, product_id):
    product = Products.objects.filter(id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect("products_page")
    return redirect("products_page")


def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    products_count = Products.objects.filter(categories=category).count()
    if request.method == "POST":
        if products_count > 0:
            messages.error(request,
                           "Enquanto exisiterem produtos com esta categoria associada, não será possível eliminá-la.")
        else:
            category.delete()
            return redirect("products_page")
    return redirect("products_page")


def delete_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)
    products_count = Products.objects.filter(suppliers=supplier).count()
    if request.method == "POST":
        if products_count > 0:
            messages.error(request,
                           "Enquanto existirem produtos associados a este fornecedor, não será possível apagá-lo.")
        else:
            supplier.delete()
            return redirect("products_page")
    return redirect("products_page")


# endregion


async def fetch_image(session, image_url):
    try:
        async with session.get(image_url) as response:
            if response.status == 200:
                return await response.read(), os.path.basename(image_url)
            else:
                return None, None
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return None, None


async def download_images(image_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url) for url in image_urls]
        return await asyncio.gather(*tasks)


def upload_excel(request):
    try:
        product_names = []
        product_links = []
        product_prices = []
        product_images = []
        product_suppliers = []
        product_categories = []
        supplier_flag = False
        category_flag = False
        suppliers = Supplier.objects.all()
        categories = Category.objects.all()
        products = Products.objects.all()

        if request.method == 'POST':
            uploaded_file = request.FILES.get('excel_file')

            if uploaded_file and uploaded_file.name.endswith('.xlsx'):
                wb = load_workbook(uploaded_file)
                ws = wb.active

                for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=6, values_only=True):
                    for col_idx, cell_value in enumerate(row, start=1):
                        if cell_value:
                            if col_idx == 1:
                                product_names.append(cell_value)
                            elif col_idx == 2:
                                product_links.append(cell_value)
                            elif col_idx == 3:
                                normalized_value = cell_value.replace(',', '.')
                                price_numeric = re.search(r'\d+[\.,]?\d*', normalized_value)
                                if price_numeric:
                                    price_float = float(price_numeric.group().replace(',', '.'))
                                    product_prices.append(price_float)
                            elif col_idx == 4:
                                product_images.append(cell_value)
                            elif col_idx == 5 and not category_flag:
                                category = categories.filter(name_category=cell_value).first()
                                if not category:
                                    categories.create(name_category=cell_value)
                                    category = categories.filter(name_category=cell_value).first()
                                product_categories.append(category)
                                category_flag = True
                                break
                            elif col_idx == 6 and not supplier_flag:
                                supplier = suppliers.filter(name_supplier=cell_value).first()
                                if not supplier:
                                    category.delete()
                                    messages.error(request,
                                                   "Este fornecedor não existe. Crie antes o fornecedor para conseguir fazer upload de produtos.")
                                    return redirect('products_page')
                                product_suppliers.append(supplier)
                                supplier_flag = True

                len_list_names = len(product_names) - 1
                product_suppliers.extend([supplier] * len_list_names)

                if len(product_names) == len(product_links) == len(product_prices) == len(product_images):
                    products_delete = products.filter(suppliers=product_suppliers[0], categories=product_categories[0])
                    products_delete.delete()

                    # Run the async image download
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    image_results = loop.run_until_complete(download_images(product_images))

                    for name, link, price, (image_content, image_name), supplier_obj in zip(product_names,
                                                                                            product_links,
                                                                                            product_prices,
                                                                                            image_results,
                                                                                            product_suppliers):
                        if image_content:
                            link_instance = Links.objects.create(url=link, price=price, supplier=supplier_obj)
                            category_obj = product_categories[0] if product_categories else None
                            product = Products.objects.create(title=name, categories=category_obj)
                            product.image.save(image_name, ContentFile(image_content), save=True)
                            product.suppliers.add(supplier_obj)
                            product.links.add(link_instance)
                            product.save()
                    messages.success(request, "Produtos importados com sucesso!")
                else:
                    category.delete()
                    messages.error(request,
                                   "Certifique-se de que o documento tem o formato certo. Existe pelo menos um produto em que falta informação.")
            else:
                messages.error(request, "Por favor, selecione um ficheiro Excel (.xlsx) para fazer o upload.")
        else:
            messages.error(request,
                           "O método de requisição não é suportado. Use o método POST para fazer o upload do arquivo.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao processar o upload: {str(e)}")

    return redirect("products_page")
