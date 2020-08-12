# -*- encoding: utf-8 -*-

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import UserModel, PasswordResetConfirmView, ValidationError, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from .forms import LoginForm
from .forms import CustomUserCreationForm


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
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ValidationError):
            user = None
        return user


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # if '@' in username:
            #     user = UserModel._default_manager.filter(
            #         email=username).first()
            #     if user is not None:
            #         username = user.username
            #     else:
            #         msg = 'Email address not found'
            # if msg is None:
            #     user = authenticate(
            #         request, username=username, password=password)
            #     if user is not None:
            #         login(request, user)
            #         return redirect('/home/')
            #     else:
            #         msg = 'Invalid credentials'
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home/')
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'
    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})


@login_required(login_url='/login/')
@staff_member_required
def register_user(request):
    msg = None
    success = False

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            msg = 'User created.'
            success = True
            # return redirect('/login/')
        else:
            msg = 'Form is not valid'
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form, 'msg': msg, 'success': success})
