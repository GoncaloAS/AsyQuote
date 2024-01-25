# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from .forms import UserProductConfigForm
# from .models import UserProductConfig, Products
# from django.views.generic.base import TemplateView
# from .models import ProductsPage
# @login_required
# def update_discount(request, product_id):
#     product = Products.objects.get(id=product_id)
#     user_config, created = UserProductConfig.objects.get_or_create(
#         user=request.user,
#         product=product
#     )
#
#     if request.method == 'POST':
#         form = UserProductConfigForm(request.POST, instance=user_config)
#         if form.is_valid():
#             form.save()
#             return redirect('product_detail', product_id=product_id)
#     else:
#         form = UserProductConfigForm(instance=user_config)
#
#     return render(request, 'builder/product_update.html', {'form': form, 'product': product})
#
#
