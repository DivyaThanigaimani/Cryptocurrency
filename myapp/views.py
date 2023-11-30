from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect

from crypto import settings
from .forms import CreateUserForm, LoginForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import Payment, StockData, UserProfile

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
from .models import StockData, Currency
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import plotly.express as px

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def homepage(request):
    return render(request, 'myapp/unregister.html')


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


@login_required(login_url="my-login")
def payment_history(request):
    payment = PaymentHistory.objects.all()
    context = {'payments': payment}
    return render(request, 'myapp/payment_history.html', context)


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


@login_required(login_url="my-login")
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
                    checkout_data["canadian_dollars"] = amount_in_cad
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


def stocks(request):
    # CoinMarketCap API endpoint for cryptocurrency listings
    api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    # Add your CoinMarketCap API key here
    api_key = '3ebb690c-aa21-4b14-bcd7-c84b1b48420e'
    search_query = request.GET.get('search', None)
    # Define parameters for the API request
    params = {
        'start': '1',
        'limit': '100',
        'convert': 'USD'
    }

    # Set headers, including the API key
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    # Make the API request
    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract relevant information from the response
        cryptocurrencies = [
            {
                'name': crypto['name'],
                'symbol': crypto['symbol'],
                'price': '${:,.2f}'.format(crypto['quote']['USD']['price']),
                'market_cap': '${:,.2f}'.format(crypto['quote']['USD']['market_cap']),
                'change_percentage': '{:.2f}'.format(crypto['quote']['USD']['percent_change_24h']),
                'volume_24h': crypto['quote']['USD']['volume_24h'],
                "volume_change_24h": crypto['quote']['USD']['volume_change_24h'],
                "percent_change_1h": crypto['quote']['USD']['percent_change_1h'],
                "percent_change_24h": crypto['quote']['USD']['percent_change_24h'],
                "percent_change_7d": crypto['quote']['USD']['percent_change_7d'],
                "percent_change_30d": crypto['quote']['USD']['percent_change_30d'],
                "percent_change_60d": crypto['quote']['USD']['percent_change_60d'],
                "percent_change_90d": crypto['quote']['USD']['percent_change_90d'],
            }
            for crypto in data['data']

        ]
        paginator = Paginator(cryptocurrencies, 10)  # Change the number to control items per page
        page = request.GET.get('page', 1)

        try:
            cryptocurrencies = paginator.page(page)
        except (
                PageNotAnInteger):
            cryptocurrencies = paginator.page(1)
        except EmptyPage:
            cryptocurrencies = paginator.page(paginator.num_pages)

        top_gainers = sorted(cryptocurrencies, key=lambda x: x['percent_change_24h'], reverse=True)[:5]
        top_losers = sorted(cryptocurrencies, key=lambda x: x['percent_change_24h'])[:5]

        show_top_gainers_and_losers = request.GET.get('show_top_gainers_and_losers', False)
        if search_query:
            search_query = search_query.lower()
            cryptocurrencies = [crypto for crypto in cryptocurrencies if search_query in crypto['name'].lower()]
    else:
        # If the API request fails, provide some default data or handle the error as needed
        cryptocurrencies = [
            {"name": "Bitcoin", "symbol": "BTC", "price": "$60,000", "market_cap": "$1.2 Trillion",
             "change_percentage": "+5"},
            # Add more default cryptocurrencies as needed
        ]
    for crypto in cryptocurrencies:
        StockData.objects.create(
            name=crypto['name'],
            symbol=crypto['symbol'],
            price=Decimal(crypto['price'].replace('$', '').replace(',', '')),
            market_cap=Decimal(crypto['market_cap'].replace('$', '').replace(',', '')),
            change_percentage=Decimal(crypto['change_percentage']),
            volume_24h=Decimal(crypto['volume_24h']),
            volume_change_24h=Decimal(crypto['volume_change_24h']),
            lasthour=Decimal(crypto['percent_change_1h']),
            last24h=Decimal(crypto['percent_change_24h']),
            week=Decimal(crypto['percent_change_7d']),
            month=Decimal(crypto['percent_change_30d']),
            TwoMonths=Decimal(crypto['percent_change_60d']),
            ThreeMonths=Decimal(crypto['percent_change_90d']),

        )
    return render(request, 'myapp/stocks.html',
                  {'cryptocurrencies': cryptocurrencies, 'top_gainers': top_gainers, 'top_losers': top_losers})


@login_required()
def stockinfo(request, stockname):
    data = StockData.objects.filter(name=stockname).first()
    settings.STOCK_NAME = stockname
    currencies = Currency.objects.all()
    if data:
        # Extract field names and values for the chart
        fields = [field.name for field in StockData._meta.get_fields() if
                  field.name not in ['id', 'name', 'date', 'name', 'price', 'market_cap', 'change_percentage',
                                     'volume_24h', 'volume_change_24h', 'volume_change_24h']]
        values = [getattr(data, field) for field in fields]
        fig = px.line(
            x=fields,
            y=[values],
            labels={'x': 'Stock Time', 'y': 'Stock Change'},
            title=f"Stock Data for {stockname}",
            line_shape='linear',  # You can change this to 'spline', 'hv', etc.
            line_dash_sequence=['solid'],  # You can customize the line dash pattern
            markers=True,  # Show markers on the lines
            # marker=dict(size=10, color='red'),  # Customize marker size and color
            template='plotly_dark',  # You can choose a different template for the plot
        )

        fig.update_layout(
            title={
                'font_size': 24,
                'anchor': 'center',
                'x': 0.5
            }
        )

        chart = fig.to_html()
        settings.CHART = chart
        settings.CONVERSION_AMOUNT = data.price
        settings.STOCK_NAME = stockname
        context = {'CHART': chart,
                   'CONVERSION_AMOUNT': data.price,
                   'STOCK_NAME': stockname,
                   'currencies': currencies,
                   'PREV_CODE': settings.PREV_CODE
                   }
    else:
        context = {
            'chart': None

        }

    return render(request, 'myapp/tradeinfo.html', context)


def convert_currency(request, amount, from_currency, to_currency):
    payload = {}
    headers = {
        "apikey": "405iqxjRNuup95vMq52Cv2cGW6d5zONh"
    }
    url = f"https://api.apilayer.com/fixer/convert?to={to_currency}&from={from_currency}&amount={amount}"
    response = requests.request("GET", url, headers=headers, data=payload)
    status_code = response.status_code
    data = response.json()
    converted_amount = data.get('result', None)
    c = Currency.objects.all()
    result = {
        'CONVERSION_AMOUNT': converted_amount,
        'currencies': c,
        'price': amount,
        'STOCK_NAME': settings.STOCK_NAME,
        'CHART': settings.CHART,
        'PREV_CODE': to_currency
    }
    settings.CONVERSION_AMOUNT = converted_amount
    settings.PREV_CODE = from_currency
    if response.status_code == 200:
        return render(request, 'myapp/tradeinfo.html', result)


    else:
        return JsonResponse({'success': False, 'error': 'Failed to retrieve data from the API'})


def register(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            username = user.username
            messages.success(request, 'Account created for ' + username)
            return redirect('my-login')

    else:
        user_form = CreateUserForm()
        profile_form = UserProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'myapp/register.html', context)

@login_required(login_url="my-login")
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        profile_pic = user_profile.profile_pic
    except UserProfile.DoesNotExist:
        profile_pic = None

    return render(request, 'myapp/dashboard.html', {'profile_pic': profile_pic})
