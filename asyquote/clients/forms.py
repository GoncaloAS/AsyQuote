from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'address', 'nif']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Insira o nome do cliente...'
        self.fields['email'].widget.attrs['placeholder'] = 'Insira o email do cliente...'
        self.fields['phone'].widget.attrs['placeholder'] = 'Insira o telemóvel do cliente...'
        self.fields['address'].widget.attrs['placeholder'] = 'Insira a morada do cliente...'
        self.fields['nif'].widget.attrs['placeholder'] = 'Insira o NIF do cliente...'

