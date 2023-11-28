# views.py
from decimal import Decimal, InvalidOperation
import requests
from django.shortcuts import render
from .forms import ExchangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SubscriptionForm

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
            country = form.cleaned_data['country']
            location = form.cleaned_data['location']
            enter_amount = form.cleaned_data['enter_amount']

            print(f"Country: {country}")
            print(f"Location: {location}")
            print(f"Enter Amount: {enter_amount}")

            try:
                # Get the exchange rate from the selected location to CAD
                exchange_rate_location_to_cad = get_exchange_rate(location.currency_code, 'CAD',
                                                                  api_key='4935f0aa1d38515190f6a29d')

                if exchange_rate_location_to_cad is not None:
                    # Perform the currency conversion to CAD
                    amount_in_cad = enter_amount * Decimal(str(exchange_rate_location_to_cad))
                    print(f"Amount in CAD: {amount_in_cad}")

                    # Prepare data to be displayed in the template
                    data = {
                        'form': form,
                        'amount_in_cad': amount_in_cad,
                    }

                    return render(request, 'exchange/exchange_form.html', data)
                else:
                    print(f"Error getting exchange rate for {location.currency_code} to CAD.")
            except InvalidOperation as ioe:
                print(f"InvalidOperation: {ioe}")

    # If the form is not valid or an exception occurred, return the form with any errors
    return render(request, 'exchange/exchange_form.html', {'form': form})
