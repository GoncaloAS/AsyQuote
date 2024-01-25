from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model, decorators
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import reverse

from asyquote.users.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://django-allauth.readthedocs.io/en/stable/advanced.html#admin
    admin.site.login = decorators.login_required(admin.site.login)  # type: ignore[method-assign]


def send_marketing_email_action(modeladmin, request, queryset):
    # Filter the queryset to include only users with receive_email set to True
    queryset = queryset.filter(receive_email=True)

    # Get the list of selected users' email addresses
    email_list = ','.join(queryset.values_list("email", flat=True))

    # Pass data to a template using the reverse function
    redirect_url = reverse('send_email_template')
    return HttpResponseRedirect(f'{redirect_url}?email_list={email_list}')


def send_review_email_action(modeladmin, request, queryset):
    # Filter the queryset to include only users with receive_email set to True
    queryset = queryset.filter(development_help=True)

    # Get the list of selected users' email addresses
    email_list = ','.join(queryset.values_list("email", flat=True))

    # Pass data to a template using the reverse function
    redirect_url = reverse('send_email_template')
    return HttpResponseRedirect(f'{redirect_url}?email_list={email_list}')


send_marketing_email_action.short_description = "Send marketing email to selected users"
send_review_email_action.short_description = "Send review email to selected users"


@admin.register(User)
class CustomUserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (_("Preferências Usuário"), {"fields": ("receive_email", "development_help")}),
        (_("Personal info"), {"fields": ("username", "email", "password")}),
        (_("Ativação Conta"), {"fields": ["acount"]}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "is_superuser"]
    search_fields = ["username"]
    actions = [send_marketing_email_action,send_review_email_action]
