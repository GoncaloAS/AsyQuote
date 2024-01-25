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
from asyquote.users.views import send_email_template
# from asyquote.products.views import update_discount
from settings_conta.views import definicoes_view, CustomPasswordResetFromKeyView, Customemail_view

urlpatterns = [
                  path("users/", include("asyquote.users.urls", namespace="users")),
                  path("accounts/", include("allauth.urls")),
                  path('send_email_template/', send_email_template, name='send_email_template'),
                  path('builder/', login_required(TemplateView.as_view(template_name='builder/builder_landing.html')),
                       name='builder'),
                  path('accounts/password/reset/key/<uidb36>/<key>/', CustomPasswordResetFromKeyView.as_view(),
                       name='account_reset_password_from_key'),
                  path('email/', Customemail_view.as_view(), name='email'),
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
