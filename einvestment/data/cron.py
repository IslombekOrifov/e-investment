import requests
from datetime import datetime

from .models import Currency, CurrencyPrice


def my_scheduled_currency():
    response = requests.get('https://nbu.uz/en/exchange-rates/json/')

    if response.status_code == 200:
        if response.json():
            list1 = []
            currency_data = [entry for entry in response.json() if entry['code'] == 'USD' or entry['code'] == 'GBP' or entry['code'] == 'EUR']
            gbp = Currency.objects.get_or_create(code='GBP', name="British Pound")
            usd = Currency.objects.get_or_create(code='USD', name="US Dollar")
            eur = Currency.objects.get_or_create(code='GBP', name="EURO")
            for data in currency_data:
                if data['code'] == 'GBP':
                    CurrencyPrice(code=data['code'], name=data['title'], cb_price=data['cb_price'], currency=gbp)
                if data['code'] == 'USD':
                    CurrencyPrice(code=data['code'], name=data['title'], cb_price=data['cb_price'], currency=usd)
                if data['code'] == 'EUR':
                    CurrencyPrice(code=data['code'], name=data['title'], cb_price=data['cb_price'], currency=eur)
            