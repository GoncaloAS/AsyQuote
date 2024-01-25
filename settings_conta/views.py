# views.py
from allauth.account.views import ConfirmEmailView, PasswordResetFromKeyView, AddEmailForm, EmailView

from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MarketingPreferencesForm


@login_required
def definicoes_view(request):
    password_change_form = PasswordChangeForm(request.user)
    marketing_preferences_form = MarketingPreferencesForm(initial={
        'development_help': request.user.development_help,
        'receive_email': request.user.receive_email,
    })

    if request.method == 'POST':
        if 'password_change_submit' in request.POST:
            # Handle password change form submission
            password_change_form = PasswordChangeForm(request.user, request.POST)
            if password_change_form.is_valid():
                password_change_form.save()
                messages.success(request, 'Você mudou a sua password com sucesso')

        elif 'marketing_preferences_submit' in request.POST:
            # Handle marketing preferences form submission
            marketing_preferences_form = MarketingPreferencesForm(request.POST)
            if marketing_preferences_form.is_valid():
                # Update the user's marketing preferences in the database
                request.user.development_help = marketing_preferences_form.cleaned_data['development_help']
                request.user.receive_email = marketing_preferences_form.cleaned_data['receive_email']
                request.user.save()
                # You can add a success message or redirect the user to a success page
                messages.success(request, 'Você mudou as suas preferências de marketing com sucesso')

    return render(request, 'builder/settings.html', {
        'password_change_form': password_change_form,
        'marketing_preferences_form': marketing_preferences_form,
        'add_email_form': AddEmailForm(),
    })


class CustomConfirmEmailView(ConfirmEmailView):
    # Override the email confirmation template name
    email_template_name = 'account/email/email_confirmation_message.html'


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(f'{self.request.path}login')


class Customemail_view(EmailView):
    success_url = '../builder/definicoes-conta/'
    def form_invalid(self, form):
        messages.error(self.request, "Este e-mail é inválido")
        return redirect('../builder/definicoes-conta')

