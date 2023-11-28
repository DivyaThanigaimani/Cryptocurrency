from django.shortcuts import render, redirect
from . forms import CreateUserForm, LoginForm
from django.contrib.auth.decorators import login_required


# Subscribe imports
from .forms import SubscriptionForm

# Contact Us imports
from django.contrib import messages
from .forms import ContactForm

# - Authentication models and functions

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def homepage(request):

    return render(request, 'myapp/index.html')

def register(request):
    form = CreateUserForm()

    if request.method == "POST":

        form = CreateUserForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return redirect("my-login")

    context = {'registerform': form}
    return render(request, 'myapp/register.html', context=context)

def my_login(request):
    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)

                return redirect("dashboard")

    context = {'loginform': form}

    return render(request, 'myapp/my-login.html', context=context)

def user_logout(request):

    auth.logout(request)

    return redirect("")
@login_required(login_url="my-login")
def dashboard(request):

    return render(request, 'myapp/dashboard.html')



def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for subscribing!')
            return redirect('landing_page')  # Replace 'landing_page' with the name of your landing page URL pattern
    else:
        form = SubscriptionForm()

    return render(request, 'subscribe.html', {'form': form})



def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('landing_page')  # Replace 'landing_page' with the name of your landing page URL pattern
    else:
        form = ContactForm()

    return render(request, 'contact_us.html', {'form': form})



