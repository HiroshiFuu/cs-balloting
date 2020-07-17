# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.contrib.auth.views import UserModel, PasswordResetConfirmView, ValidationError, urlsafe_base64_decode
from django.contrib.auth.hashers import check_password

from .forms import LoginForm, CustomUserCreationForm
from .models import CompanyUser


# Create your views here.
class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except UserModel.DoesNotExist:
            print('UserModel.DoesNotExist')
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CompanyUser._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ValidationError):
            user = None
        return user


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            print(username, password)
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home/')
            elif UserModel._default_manager.filter(username=username).first() is None:
                print('Custom Login')
                user = CompanyUser.objects.filter(username=username).first()
                if user is not None:
                    pw_valid = check_password(password, user.password)
                    if pw_valid:
                        user = UserModel._default_manager.get(username='company_user')
                        login(request, user)
                        return redirect('/home/')
                    else:
                        msg = 'Invalid credentials'
                else:
                    msg = 'Invalid username'
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})


def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = 'User created.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form is not valid'    
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })
