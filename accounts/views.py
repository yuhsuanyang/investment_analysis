import pandas as pd
from datetime import datetime
from django.shortcuts import render, redirect
from pathlib import Path
from .models import Account
from transactions.models import TransactionData
from stock_prices.models import StockPriceData
from utils import queryset2df

ROOT = Path(__file__).resolve().parent.parent
stock_codes = pd.read_csv(f'{ROOT}/stock_prices/stock_codes.csv',
                          usecols=['code', 'name'],
                          dtype=str)


# Create your views here.
def account_form(request):
    data = {}
    if request.method == "POST":
        name = request.POST['acc_name']
        date = datetime.today().date()
        new_account = Account(name=name,
                              record_date=date,
                              realized_profit=0,
                              unrealized_profit=0,
                              cost=0)
        new_account.save()
        print(f"account {name} created!")
        return render(request,
                      'account_success_message.html',
                      context={
                          'name': name,
                      })


#        return redirect('/new_account')
    return render(request, 'new_account.html', context=data)


def delete_account(request):
    if request.method == 'POST':
        name = request.POST['account']

    acc = Account.objects.filter(name=name)
    not_acc_codes = TransactionData.objects.all().exclude(
        account=acc[0].name).values('code').distinct()
    stock_codes = StockPriceData.objects.all()
    deleted_codes = stock_codes.values('code').distinct()
    deleted_codes = [
        code['code'] for code in deleted_codes if code not in not_acc_codes
    ]
    print(deleted_codes)

    acc.delete()
    TransactionData.objects.all().filter(account=name).delete()
    for code in deleted_codes:
        stock_codes.filter(code=code).delete()
        print(f"{code} delete")

    return render(request, 'delete_account.html', context={'account': name})


def display_stocks(requests, account):
    with open(f"{ROOT}/stock_prices/data_date_record.txt", 'r') as f:
        record_date = f.read().strip()

    transactions = TransactionData.objects.all().filter(account=account)
    transaction_df = queryset2df(transactions).sort_values('code').reset_index(
        drop=True)
    all_prices = StockPriceData.objects.all().order_by('-date')
    print(transaction_df)
    transaction_by_stock = []
    for code in transaction_df['code'].unique():
        name = stock_codes[stock_codes['code'] == code]['name'].iloc[0]
        df = transaction_df[transaction_df['code'] == code]
        details = []
        for i in range(len(df)):
            details.append([
                datetime.strftime(df.iloc[i]['date'], '%Y-%m-%d'),
                df.iloc[i]['price'], df.iloc[i]['amount'], df.iloc[i]['fee']
            ])

        price = all_prices.filter(code=code)[0]
        latest_value = round(price.price * df['amount'].sum() *
                             (1 - 0.003 - 0.001425))
        cost = (df['price'] * df['amount'] + df['fee']).sum()
        transaction_by_stock.append([
            f"{code} {name}", df['amount'].sum(), cost,
            round(cost / df['amount'].sum(), 2),
            round(price.price, 2), latest_value,
            round(latest_value - cost, 2),
            round(100 * (latest_value - cost) / cost, 2), details
        ])
    data = {
        'name': account,
        'data': transaction_by_stock,
        'data_date': record_date
    }
    return render(requests, 'account.html', context=data)
