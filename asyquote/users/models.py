from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, BooleanField

from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for AsyQuote.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    receive_email = BooleanField(_("Receber emails "), blank=True, max_length=255, default=False)
    development_help = BooleanField(_("Ajudar no desenvolvimento "), blank=True, max_length=255, default=False)
    acount = BooleanField(_("Ativar conta usuário"), blank=True, max_length=255, default=False)
    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
