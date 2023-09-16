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
                    date_str = data['date']
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
                    list1.append(CurrencyPrice(code=data['code'], name=data['title'], cb_price=data['cb_price'], date=date_obj.date(), currency=gbp))
                if data['code'] == 'USD':
                    date_str = data['date']
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
                    list1.append(CurrencyPrice(code=data['code'], name=data['title'], cb_price=data['cb_price'], date=date_obj.date(), currency=usd))
                if data['code'] == 'EUR':
                    date_str = data['date']
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
                    list1.append(CurrencyPrice(code=data['code'], name=data['title'], cb_price=data['cb_price'], date=date_obj.date(), currency=eur))
            CurrencyPrice.objects.bulk_create(list1)