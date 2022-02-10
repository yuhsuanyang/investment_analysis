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
        stock_code = request.POST['stock_code']
        date = request.POST['date']
        account = request.POST['account']
        stock_price = request.POST['stock_price']
        stock_amount = request.POST['stock_amount']
        fee = request.POST['fee']
        transaction = TransactionData(code=stock_code.split(' ')[0],
                                      date=date,
                                      account=account,
                                      price=stock_price,
                                      amount=stock_amount,
                                      fee=fee)
        #        print(stock_code, date, account, stock_price, stock_amount, fee)
        #        print(transaction)
        transaction.save()
        #        data = TransactionData.objects.all()
        #        print(data)
        return render(request,
                      'success_message.html',
                      context={
                          'code': stock_code,
                          'amount': stock_amount,
                          'price': stock_price
                      })
    data = {'accounts': accounts, 'stock_codes': stock_codes['code'].tolist()}
    return render(request, 'new_transaction.html', context=data)
