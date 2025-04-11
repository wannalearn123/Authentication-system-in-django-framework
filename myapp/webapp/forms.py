from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # captcha = ReCaptchaField()  # Add CAPTCHA field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',] #'captcha'

# class LoginForm(AuthenticationForm):
#     captcha = ReCaptchaField()  # Add CAPTCHA field

#     class Meta:
#         fields = ['username', 'password', 'captcha']