from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from allauth.account.views import SignupView, LoginView, LogoutView
from django.contrib.auth.decorators import login_required

from asyquote.clients.views import client_list, create_client, update_client, delete_client, filter_clients
from asyquote.products.views import ProductsPageView, NotFoundProductView, filter_products, create_product, \
    create_category, create_supplier, update_supplier, update_category, update_product
from asyquote.projects.views import project_list, create_project, edit_project, filter_projects, list_projects_table, \
    download_excel, filter_projects_data, delete_project, update_project, save_quote_url
from asyquote.users.views import send_email_template
from settings_conta.views import definicoes_view, CustomPasswordResetFromKeyView, CustomEmailView

urlpatterns = [
                  path("users/", include("asyquote.users.urls", namespace="users")),
                  path("accounts/", include("allauth.urls")),
                  path('send_email_template/', send_email_template, name='send_email_template'),
                  path('builder/products/', login_required(ProductsPageView.as_view()), name='products_page'),
                  path('builder/products/create/', create_product, name='create-product'),
                  path('builder/products/category/create/', create_category, name='create-category'),
                  path('builder/products/supplier/create/', create_supplier, name='create-supplier'),
                  path('builder/products/supplier/update/<int:supplier_id>', update_supplier, name='update-supplier'),
                  path('builder/products/product/update/<int:product_id>', update_product, name='update-product'),
                  path('builder/products/category/update/<int:category_id>', update_category, name='update-category'),
                  path('filter-products/', filter_products, name='filter_products'),
                  path('404/products', NotFoundProductView.as_view(), name='404-products'),
                  path('builder/projects/', project_list, name='project_list'),
                  path('builder/clients/', client_list, name='client_list'),
                  path('builder/projects/create/', create_project, name='create_project'),
                  path('builder/projects/update/<int:project_id>/', update_project, name='update_project'),
                  path('builder/projects/delete/<int:project_id>/', delete_project, name='delete_project'),
                  path('builder/clients/create/', create_client, name='create_client'),
                  path('builder/clients/update/<int:client_id>/', update_client, name='update_client'),
                  path('builder/clients/delete/<int:client_id>/', delete_client, name='delete_client'),
                  path('builder/projects/edit/<uuid:key>/', edit_project, name='edit_project'),
                  path('savequote/', save_quote_url, name='save_quote'),

                  path('filter_projects/', filter_projects, name='filter_projects'),
                  path('filter_projects_data/', filter_projects_data, name='filter_projects_data'),
                  path('filter_clients/', filter_clients, name='filter_clients'),
                  path('builder/projects/list/', list_projects_table, name='list_projects_table'),
                  path('builder/projects/list/download/', download_excel, name='download_excel'),
                  path('accounts/password/reset/key/<uidb36>/<key>/', CustomPasswordResetFromKeyView.as_view(),
                       name='account_reset_password_from_key'),
                  path('email/', CustomEmailView.as_view(), name='email'),
                  path('builder/definicoes-conta/', definicoes_view, name='definicoes'),
                  # path('builder/produtos/update/<int:product_id>/', update_discount, name='update_discount'),
                  path('aceder-beta/', SignupView.as_view(), name='aceder-beta'),
                  path('login/', LoginView.as_view(), name='login'),
                  path('logout/', login_required(LogoutView.as_view()), name='logout'),
                  path(settings.ADMIN_URL, include(wagtailadmin_urls)),
                  path('django-admin/', admin.site.urls),
                  path('', include(wagtail_urls)),

                  # User management

                  # Your stuff: custom urls includes go here
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
