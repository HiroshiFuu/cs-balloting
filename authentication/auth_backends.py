# -*- encoding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if '@' in username:
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                return None, 'Email address not found'
            else:
                if user.check_password(password):
                    return user
        else:
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None, 'Username not found'
            else:
                if user.check_password(password):
                    return user
        return None
