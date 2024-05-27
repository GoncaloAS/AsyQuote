from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
import uuid
from wagtail.models import Page
from django.db.models import Sum
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from asyquote.clients.models import Client


class Project(models.Model):
    STATE_CHOICES = [
        ('CONCLUÍDO', 'Concluído'),
        ('PERDIDO', 'Perdido'),
        ('EM ESPERA', 'Em Espera'),
        ('EM EXECUÇÃO', 'Em execução'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quote_number = models.CharField(_('Número do Orçamento'), max_length=100)
    image = models.ImageField(upload_to='project_images/', verbose_name='Image', null=True, blank=True)
    title = models.CharField(_('Titulo'), max_length=100)
    address = models.CharField(_('Morada'), max_length=200)
    client = models.ForeignKey(Client, verbose_name=_('Cliente'), on_delete=models.CASCADE)
    value = models.DecimalField(_('Valor'), max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    state = models.CharField(_('Estado'), max_length=20, choices=STATE_CHOICES)
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            while True:
                self.key = uuid.uuid4()
                if not Project.objects.filter(key=self.key).exists():
                    break
            Notes.objects.create(project_key=self.key)
        super().save(*args, **kwargs)

    def total_cost(self):
        return PricesQuote.objects.filter(project_key=self.key).aggregate(total_cost=Sum('cost'))['total_cost'] or 0

    def total_charged(self):
        return PricesQuote.objects.filter(project_key=self.key).aggregate(total_charged=Sum('charged'))['total_charged'] or 0

    def profit_percentage(self):
        total_cost = self.total_cost()
        total_charged = self.total_charged()
        if total_cost == 0:
            return 0
        return ((total_charged - total_cost) / total_cost) * 100


class SectionQuote(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    project_key = models.UUIDField(default=uuid.uuid4, editable=False)
    section_count = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True, default=1)
    visible = models.BooleanField(default=True)


class ServicesQuote(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.CharField(max_length=255, null=True, blank=True)
    project_key = models.UUIDField(default=uuid.uuid4, editable=False)
    section_key = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    service_count = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True, default=1)
    visible = models.BooleanField(default=True)


class PricesQuote(models.Model):
    description = models.CharField(max_length=255, null=True, blank=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    charged = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    profit_money = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    profit_percentage = models.CharField(max_length=255, null=True, blank=True)
    project_key = models.UUIDField(default=uuid.uuid4, editable=False)
    section_key = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    services_key = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    prices_count = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True, default=1)
    visible = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.cost is not None and self.charged is not None:
            if int(self.cost) == 0:
                profit = self.charged
                percentage = profit * 100
            else:
                profit = float(self.charged or 0) - float(self.cost or 0)
                percentage = (profit / float(self.cost)) * 100
            self.profit_money = profit

            self.profit_percentage = str(percentage)

        super(PricesQuote, self).save(*args, **kwargs)


class Notes(models.Model):
    notes = models.CharField(max_length=255, null=True, blank=True)
    project_key = models.UUIDField(default=uuid.uuid4, editable=False)

