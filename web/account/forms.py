from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
