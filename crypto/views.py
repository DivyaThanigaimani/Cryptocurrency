from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import plotly.express as px
import requests
from django.shortcuts import render

from django.urls import reverse

from django import forms
from .models import StockData, Currency
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


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


def home(request):
    currencies = Currency.objects.all()
    context = {'currencies': currencies}
    return render(request, 'myapp/home.html', context)


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


def user_logout(request):
    logout(request)
    return redirect('home')
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
        except PageNotAnInteger:
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





# def contact(request):
#     if request.method=="POST":
#
#
#
#     return HTTPResponse("<h1> THANKS FOR CONTACTING US</h1>")
# return render(request,'contact.html')



from django.shortcuts import render

# Create your views here.
