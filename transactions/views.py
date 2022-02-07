import pandas as pd
from pathlib import Path
from django.shortcuts import render, redirect
from accounts.models import Account
from .models import TransactionData

ROOT = Path(__file__).resolve().parent.parent
stock_codes = pd.read_csv(f'{ROOT}/stock_prices/stock_codes.csv',
                          usecols=['code', 'name'],
                          dtype=str)
stock_codes['code'] = stock_codes['code'] + ' ' + stock_codes['name']


# Create your views here.
def main(request):
    data = {'message': 'hi'}
    return render(request, 'index.html', context=data)


def transaction_form(request):
    accounts = [acc.name for acc in Account.objects.all()]
    print(ROOT)
    if not len(accounts):
        return render(request, 'warning_no_account.html', context={})

    if request.method == "POST":
        stock_code = request.POST['stock_code'].split(' ')[0]
        date = request.POST['date']
        account = request.POST['account']
        stock_price = request.POST['stock_price']
        stock_amount = request.POST['stock_amount']
        fee = request.POST['fee']
        print(stock_code, date, account, stock_price, stock_amount, fee)
        return redirect('/new_transaction')
    data = {'accounts': accounts, 'stock_codes': stock_codes['code'].tolist()}
    return render(request, 'new_transaction.html', context=data)
