from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _


class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(_('Nome'), max_length=100)
    email = models.EmailField(_('Email'), max_length=200)
    phone = models.CharField(_('Telefone'), max_length=100)
    address = models.CharField(_('Morada'), max_length=200)
    nif = models.CharField(_('NIF'), max_length=9)
    value = models.CharField(_('Valor'), null=True, blank=True, default=0)

    def __str__(self):
        return self.name
