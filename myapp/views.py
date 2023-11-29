from django.shortcuts import render, redirect

from crypto import settings
from . forms import CreateUserForm, LoginForm
from django.contrib.auth.decorators import login_required
from .models import Payment

# Subscribe imports
from .forms import SubscriptionForm

# Contact Us imports
from django.contrib import messages
from .forms import ContactForm

# Glossary imports
from django.shortcuts import render
from .models import GlossaryTerm

# - Authentication models and functions

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

from decimal import Decimal, InvalidOperation
import requests
from django.shortcuts import render
from .forms import ExchangeForm

import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from stripe import Price

from .models import PaymentHistory

stripe.api_key = settings.STRIPE_SECRET_KEY

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



def contact_us(request):
    success_message = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():

            contact_message = form.save(commit=False)
            contact_message.save()
            success_message = "Thank you for contacting us. We'll reach out to you shortly!"
            form = ContactForm()
    else:
        form = ContactForm()

    return render(request, 'contact_us.html', {'form': form, 'success_message': success_message})



def glossary_view(request):
    glossary_terms = GlossaryTerm.objects.all()
    context = {'glossary_terms': glossary_terms}
    return render(request, 'myapp/glossary.html', context)

def payment_history(request):
    payment = PaymentHistory.objects.all()
    context = {'payments': payment}
    return render(request, 'myapp/dashboard.html', context)
	
def get_exchange_rate(base_currency, target_currency, api_key):
    url = f'https://open.er-api.com/v6/latest/{base_currency}?apikey={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        # Check if the target currency is in the rates
        if target_currency not in data['rates']:
            print(f"Error: Target currency {target_currency} not found in API response.")
            return None

        return data['rates'][target_currency]
    except requests.exceptions.RequestException as err:
        print(f"Error making API request: {err}")

    # Return a default value or handle the error as appropriate for your application
    return None


def exchange_view(request):
    form = ExchangeForm()

    if request.method == 'POST':
        form = ExchangeForm(request.POST)
        if form.is_valid():
            # Get data from the form
            checkout_data = {
                'name': 'Divya',
                'destination_country': form.cleaned_data['country'],
                'amount': str(form.cleaned_data['enter_amount']),
                'pickup_location': form.cleaned_data['location'],
                'province': form.cleaned_data['province'],
                'region': form.cleaned_data['region'],
            }

            location = form.cleaned_data['location']
            enter_amount = form.cleaned_data['enter_amount']


            try:
                # Get the exchange rate from the selected location to CAD
                exchange_rate_location_to_cad = get_exchange_rate(location.currency_code, 'CAD',
                                                                  api_key='4935f0aa1d38515190f6a29d')

                if exchange_rate_location_to_cad is not None:
                    # Perform the currency conversion to CAD
                    amount_in_cad = enter_amount * Decimal(str(exchange_rate_location_to_cad))
                    print(f"Amount in CAD: {amount_in_cad}")
                    checkout_data["canadian_dollars"]=amount_in_cad
                    PaymentHistory.objects.create(
                        name=checkout_data['name'],
                        destination=checkout_data['destination_country'],
                        debited=amount_in_cad,
                        status="completed",
                        currency=location,
                        exchangedamt=checkout_data['amount'],
                        pickuplocation=checkout_data['province'],
                        province=checkout_data['province'],
                        region=checkout_data['region'],
                    )
                    return render(request, 'currency_summary.html',
                                  {'checkout_data': checkout_data})
                else:
                    print(f"Error getting exchange rate for {location.currency_code} to CAD.")
            except InvalidOperation as ioe:
                print(f"InvalidOperation: {ioe}")
    else:

     return render(request, 'exchangeform.html', {'form': form})

class CreateStripeCheckoutSessionView(View):
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """

    def post(self, request, *args, **kwargs):
       # price = self.kwargs["pk"]
        price = request.POST.get('canadian_dollars')

        price = Decimal(price)
        checkout_data = request.session.get('checkout_data', None)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(price * 100),
                        "product_data": {
                            "name": "Currency",
                            "description": "Currency",
                        },
                    },
                    "quantity": 1,
                }
            ],
            metadata=checkout_data,
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        return redirect(checkout_session.url)

class SuccessView(TemplateView):
    template_name = "success.html"

