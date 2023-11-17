from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.forms import CharField, ChoiceField, BooleanField
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    development_help = BooleanField(
        label="Aceita ajudar no desenvolvimento do asyquote?",
        required=False
    )
    receive_email = BooleanField(
        label="Deseja receber e-mails sobre as novidades da ferramenta?",
        required=False
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(), label="Captcha")

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields['development_help'].initial = False  # Set default value if needed
        self.fields['receive_email'].initial = False  # Set default value if needed

    def save(self, request):
        # Call the superclass's save method
        user = super(UserSignupForm, self).save(request)

        # Save the additional fields to the user instance
        user.development_help = self.cleaned_data['development_help']
        user.receive_email = self.cleaned_data['receive_email']
        user.save()

        self.send_signup_confirmation_email(user)

        return user

    def send_signup_confirmation_email(self, user):
        subject = 'Thank you for signing up'
        message = render_to_string('signup_confirmation_email.txt', {'user': user})
        plain_message = strip_tags(message)
        from_email = 'goncaloalves0530@gmail.com'
        to_email = [user.email]

        send_mail(subject, plain_message, from_email, to_email, html_message=message)

    field_order = ['email', 'username', 'password1', 'password2', 'development_help', 'receive_email', 'captcha']


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
