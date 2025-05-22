from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import *
import datetime
from django.template.loader import render_to_string
from django.conf import settings
from pathlib import Path
import subprocess


def index(request):
    # Reroute the user to the home page if they are logged in.
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main:index'))
    
    # Check that the user has not been locked out before rerouting to login page. 
    else:
        return HttpResponseRedirect(reverse('account:login_page'))


def login_page(request):
    # Create teh context dictionary.     
    context = {'login_form': LoginForm(), 'message': 'Please log in to contine.'}

    # Display the form if it is a GET request.
    if request.method == "GET":
        return render(request, 'account/login_page.html', context=context)
    
    # Process the form if it is a POST request.
    elif request.method == "POST":
        login_form = LoginForm(request.POST)
        data = {}
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            # A successful login via Django's built in authentication
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('main:index'))
            # Check how many login attempts have been made.
            else:
                context['message'] = f"Incorrect username or password. Please try again"
        return render(request, 'account/login_page.html', context=context)
    

def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('account:index'))