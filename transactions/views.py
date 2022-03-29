import pandas as pd
from pathlib import Path
from django.shortcuts import render
from accounts.models import Account
from stock_prices.views import initial_stock_price  # remember ad this to buy
from utils import queryset2df
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


def buy_transaction_form(request):
    accounts = [acc.name for acc in Account.objects.all()]
    print(ROOT)
    if not len(accounts):
        return render(request, 'warning.html', context={'message': '您尚未新增帳戶！'})

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
                      'transaction_success_message.html',
                      context={
                          'code': stock_code,
                          'amount': stock_amount,
                          'price': stock_price
                      })
    data = {
        'accounts': accounts,
        'stock_codes': stock_codes['code'].tolist(),
        'color': 'pink'
    }
    return render(request, 'new_transaction.html', context=data)


def sell_transaction_form(request):
    accounts = [acc.name for acc in Account.objects.all()]
    if request.method == "POST":
        stock_code = request.POST['stock_code']
        date = request.POST['date']
        account = request.POST['account']
        stock_price = request.POST['stock_price']
        stock_amount = request.POST['stock_amount']
        fee = request.POST['fee']

        transaction_records = TransactionData.objects.all().filter(
            account=account).filter(code=stock_code)
        if not len(transaction_records) or queryset2df(
                transaction_records)['amount'].sum() < stock_amount:  # 庫存量不足
            return render(request,
                          'warning.html',
                          context={'message': f'{stock_code}庫存量不足！'})

        transaction = TransactionData(code=stock_code.split(' ')[0],
                                      date=date,
                                      account=(-1) * account,
                                      price=stock_price,
                                      amount=stock_amount,
                                      fee=fee)
        transaction.save()

        transaction_records = TransactionData.objects.all().filter(
            account=account).filter(code=stock_code)
        transaction_df = queryset2df(transaction_records)
        if not transaction_df['amount'].sum():  #全部賣出 加到已實現損益
            #            transaction_records.delete()

            print('sold out')

    data = {
        'accounts': accounts,
        'stock_codes': stock_codes['code'].tolist(),
        'color': 'lime'
    }
    return render(request, 'new_transaction.html', context=data)
