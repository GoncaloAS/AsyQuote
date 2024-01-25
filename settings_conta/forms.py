from django import forms


class MarketingPreferencesForm(forms.Form):
    receive_email = forms.BooleanField(
        label="Deseja receber email sobre as novidades da ferramenta?",
        required=False
    )
    development_help = forms.BooleanField(
        label="Aceita ajudar no desenvolvimento do asyquote?",
        required=False
    )



