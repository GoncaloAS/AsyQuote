from allauth.account.views import LoginView, LogoutView, SignupView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views import defaults as default_views
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from asyquote.clients.views import ClientListView, create_client, delete_client, filter_clients, update_client
from asyquote.products.views import (
    NotFoundProductView,
    ProductsListView,
    create_category,
    create_product,
    create_supplier,
    delete_category,
    delete_product,
    delete_supplier,
    filter_products,
    update_category,
    update_product,
    update_supplier,
    upload_excel,
)
from asyquote.projects.views import (
    create_fields_quote,
    create_project,
    delete_fields_quote,
    delete_project,
    download_excel,
    download_project_quote,
    edit_project,
    filter_edit_products,
    filter_projects,
    filter_projects_data,
    list_projects_table,
    project_list,
    save_quote_data,
    save_quote_url,
    update_project,
)
from asyquote.users.views import send_email_template
from settings_conta.views import CustomEmailView, CustomPasswordResetFromKeyView, definicoes_view

urlpatterns = [
    path("users/", include("asyquote.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("send_email_template/", send_email_template, name="send_email_template"),
    path("builder/products/", login_required(ProductsListView.as_view()), name="products_page"),
    path("builder/products/create/", create_product, name="create-product"),
    path("builder/products/category/create/", create_category, name="create-category"),
    path("builder/products/supplier/create/", create_supplier, name="create-supplier"),
    path("builder/products/supplier/update/<int:supplier_id>", update_supplier, name="update-supplier"),
    path("builder/products/product/update/<int:product_id>", update_product, name="update-product"),
    path("builder/products/category/update/<int:category_id>", update_category, name="update-category"),
    path("builder/products/delete/<int:product_id>/", delete_product, name="delete-product"),
    path("builder/products/category/delete/<int:category_id>/", delete_category, name="delete-category"),
    path("builder/products/supplier/delete/<int:supplier_id>/", delete_supplier, name="delete-supplier"),
    path("builder/products/excel_upload/", upload_excel, name="upload-excel"),
    path("filter-products/", filter_products, name="filter_products"),
    path("filter-edit-products/", filter_edit_products, name="filter_edit_products"),
    path("404/products", NotFoundProductView.as_view(), name="404-products"),
    path("builder/projects/", project_list, name="project_list"),
    path("builder/clients/", ClientListView.as_view(), name="client_list"),
    path("builder/projects/create/", create_project, name="create_project"),
    path("builder/projects/update/<int:project_id>/", update_project, name="update_project"),
    path("builder/projects/delete/<uuid:key>/", delete_project, name="delete_project"),
    path("builder/clients/create/", create_client, name="create_client"),
    path("builder/clients/update/<int:client_id>/", update_client, name="update_client"),
    path("builder/clients/delete/<int:client_id>/", delete_client, name="delete_client"),
    path("builder/projects/edit/<uuid:key>/", edit_project, name="edit_project"),
    path("savequote/", save_quote_url, name="save_quote"),
    path("savequotedata/", save_quote_data, name="save_quote_data"),
    path("delete_fields_quote", delete_fields_quote, name="delete_fields_quote"),
    path("create_fields_quote", create_fields_quote, name="create_fields_quote"),
    path("download_project_quote/<uuid:project_key>/", download_project_quote, name="download_project_quote"),
    path("filter_projects/", filter_projects, name="filter_projects"),
    path("filter_projects_data/", filter_projects_data, name="filter_projects_data"),
    path("filter_clients/", filter_clients, name="filter_clients"),
    path("builder/projects/list/", list_projects_table, name="list_projects_table"),
    path("builder/projects/list/download/", download_excel, name="download_excel"),
    path(
        "accounts/password/reset/key/<uidb36>/<key>/",
        CustomPasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
    path("email/", CustomEmailView.as_view(), name="email"),
    path("builder/definicoes-conta/", definicoes_view, name="definicoes"),
    # path('builder/produtos/update/<int:product_id>/', update_discount, name='update_discount'),
    path("aceder-beta/", SignupView.as_view(), name="aceder-beta"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", login_required(LogoutView.as_view()), name="logout"),
    path(settings.ADMIN_URL, include(wagtailadmin_urls)),
    path("django-admin/", admin.site.urls),
    path("", include(wagtail_urls)),
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
