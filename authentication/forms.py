# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from .models import AuthUser
from .models import Company

from .constants import USER_TYPES
from .constants import USER_TYPE_COMPANY
from .constants import USER_TYPE_USER


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


def gen_random_password():
    return AuthUser.objects.make_random_password() + '!2Wq'


class CustomCompanyCreationForm(UserCreationForm):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    random_password = gen_random_password()
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': '',
                'class': 'form-control'
            }
        ),
        required=True
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "off",
                "class": "form-control",
            },
            render_value=True),
        help_text=password_validation.password_validators_help_text_html(),
        initial=random_password,
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password Confirmation",
                "autocomplete": "off",
                "class": "form-control"
            },
            render_value=True),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        initial=random_password,
    )
    is_staff = forms.BooleanField(
        label="Is Company User",
        initial=True,
        required=False,
    )

    class Meta:
        model = AuthUser
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    random_password = gen_random_password()

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "",
                "class": "form-control"
            }
        ),
        required=True
    )
    weight = forms.IntegerField(
        required=True
    )
    # user_type = forms.ChoiceField(
    #     choices=USER_TYPES,
    #     initial=USER_TYPE_USER,
    #     required=True,
    #     disabled=True
    # )
    # company_user = forms.ModelChoiceField(
    #     queryset=AuthUser.objects.all().filter(user_type=USER_TYPE_COMPANY, is_staff=True, is_active=True),
    #     required=True,
    #     disabled=True
    # )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
            "autocomplete": "off",
            "class": "form-control"},
            render_value=True),
        help_text=password_validation.password_validators_help_text_html(),
        initial=random_password,
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password Confirmation",
            "autocomplete": "off",
            "class": "form-control"},
            render_value=True),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        initial=random_password,
    )

    class Meta:
        model = AuthUser
        fields = ('password1', 'password2')
