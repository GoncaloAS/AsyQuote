from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    image = forms.ImageField(required=False)

    class Meta:
        model = Project
        fields = ['quote_number', 'title', 'address', 'client', 'image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Insira um título para o seu projeto...'
        self.fields['address'].widget.attrs['placeholder'] = 'Insira a morada do seu projeto...'

        if user:
            last_user_quote = Project.objects.filter(user=user).order_by('-quote_number').first()
            if last_user_quote:
                next_quote_number = int(last_user_quote.quote_number) + 1
            else:
                next_quote_number = 1

            self.fields['quote_number'].initial = next_quote_number
            self.fields['quote_number'].widget.attrs['readonly'] = True
            self.fields['quote_number'].widget.attrs['placeholder'] = f'Próximo número disponível: {next_quote_number}'

