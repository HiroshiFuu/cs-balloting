# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",
                "class": "form-control"
            }
        ))


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder' : 'Username',
                'class': 'form-control'
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder' : 'Email',
                'class': 'form-control'
            }
        ))
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder' : 'Password',
            'autocomplete': 'new-password',
            'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={
            'placeholder' : 'Password Confirmation',
            'autocomplete': 'new-password',
            'class': 'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
    # password1 = forms.CharField(
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder' : 'Password',
    #             'class': 'form-control'
    #         }
    #     ))
    # password2 = forms.CharField(
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder' : 'Password Confirmation',
    #             'class': 'form-control'
    #         }
    #     ))
    weight = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder' : 'Vote Weighting',
                'class': 'form-control'
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'weight', 'password1', 'password2')