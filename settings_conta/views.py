# views.py
from allauth.account.views import ConfirmEmailView, PasswordResetFromKeyView, AddEmailForm, EmailView

from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MarketingPreferencesForm
from django.http import JsonResponse
from django.contrib import messages


@login_required
def definicoes_view(request):
    password_change_form = PasswordChangeForm(request.user)
    marketing_preferences_form = MarketingPreferencesForm(initial={
        'development_help': request.user.development_help,
        'receive_email': request.user.receive_email,
    })
    if request.method == 'POST':
        if request.POST.get('form_type_password') == 'password_change_submit':
            password_change_form = PasswordChangeForm(request.user, request.POST)
            if password_change_form.is_valid():
                password_change_form.save()
                return JsonResponse({'success': True, 'message': 'Palavra passe mudada com sucesso'})

            else:
                errors_message = ""
                if password_change_form.errors:
                    for errors in password_change_form.errors.values():
                        errors_message += f"{errors[0]}."
                        break
                return JsonResponse(
                    {'error': True,
                     'message': errors_message})




        elif request.POST.get('form_type_marketing') == 'marketing_preferences_submit':
            marketing_preferences_form = MarketingPreferencesForm(request.POST)
            if marketing_preferences_form.is_valid():
                request.user.development_help = marketing_preferences_form.cleaned_data['development_help']
                request.user.receive_email = marketing_preferences_form.cleaned_data['receive_email']
                request.user.save()

    return render(request, 'builder/settings.html', {
        'password_change_form': password_change_form,
        'marketing_preferences_form': marketing_preferences_form,
        'add_email_form': AddEmailForm(),

    })


class CustomConfirmEmailView(ConfirmEmailView):
    email_template_name = 'account/email/email_confirmation_message.html'


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect('../../../../../../../login')


class CustomEmailView(EmailView):
    success_url = '../builder/definicoes-conta/'

    def form_invalid(self, form):
        messages.error(self.request, "Este e-mail é inválido")
        return redirect('../builder/definicoes-conta')
