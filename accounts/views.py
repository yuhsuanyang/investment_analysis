import pandas as pd
from datetime import datetime
from django.shortcuts import render, redirect
from pathlib import Path
from .models import Account
from transactions.models import TransactionData, RealizedProfit
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
        if not len(name):
            msg = '帳戶名不可為空!'
        else:
            new_account = Account(name=name)
            new_account.save()
            msg = f"已新增帳戶{name}!"
        print(msg)
        return render(request,
                      'account_success_message.html',
                      context={
                          'msg': msg,
                      })


#        return redirect('/new_account')
    return render(request, 'new_account.html', context=data)


def cal_left_overs(buy_df, sold_amount):
    for i in range(len(buy_df)):
        stock_amount = buy_df.iloc[i]['amount']
        buy_fee = buy_df.iloc[i]['fee']
        if sold_amount >= stock_amount:
            buy_df.loc[i, 'amount'] = 0
            sold_amount -= stock_amount
        else:
            buy_df.loc[i, 'amount'] = stock_amount - sold_amount
            buy_df.loc[i, 'fee'] = buy_fee * (1 - sold_amount / stock_amount)
            break
    return buy_df


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


def display_unrealized_profit(account):
    transactions = TransactionData.objects.all().filter(account=account)
    if not len(transactions):
        empty = pd.DataFrame([])
        return empty, empty
    transaction_df = queryset2df(transactions).sort_values('code').reset_index(
        drop=True)
    all_prices = StockPriceData.objects.all().order_by('-date')
    #    print(transaction_df)
    # unrealized profit
    transaction_by_stock = []
    for code in transaction_df['code'].unique():
        name = stock_codes[stock_codes['code'] == code]['name'].iloc[0]
        df = transaction_df[transaction_df['code'] == code]
        print(df)
        print('-' * 20)
        buy_df = df[df['amount'] > 0].reset_index(drop=True)
        sold_amount = df[df['amount'] < 0]['amount'].sum() * (-1)
        if not df['amount'].sum():
            continue
        else:
            buy_df = cal_left_overs(buy_df, sold_amount)


#            print(buy_df)

        details = []
        for i in range(len(df)):
            details.append([
                datetime.strftime(df.iloc[i]['date'], '%Y-%m-%d'),
                df.iloc[i]['price'], df.iloc[i]['amount'], df.iloc[i]['fee']
            ])

        price = all_prices.filter(code=code)[0]
        latest_value = round(price.price * df['amount'].sum() *
                             (1 - 0.003 - 0.001425))
        cost = (buy_df['price'] * buy_df['amount'] + buy_df['fee']).sum()
        transaction_by_stock.append([
            f"{code} {name}", df['amount'].sum(), cost,
            round(cost / df['amount'].sum(), 2),
            round(price.price, 2), latest_value,
            round(latest_value - cost, 2),
            round(100 * (latest_value - cost) / cost, 2), details
        ])
    return transaction_df, transaction_by_stock


def display_profits(requests, account):
    with open(f"{ROOT}/stock_prices/data_date_record.txt", 'r') as f:
        record_date = f.read().strip()
    transaction_df, unrealized_profit = display_unrealized_profit(account)
    if not len(transaction_df):
        data = {'name': account}
        return render(requests, 'account.html', context=data)


#    account_records = Account.objects.filter(name=account)
    account_records = RealizedProfit.objects.filter(account=account)
    sold_stock = transaction_df[transaction_df['amount'] < 0]
    realized_profit = []
    for i in range(len(sold_stock)):
        #        profit = account_records.filter(
        #            record_date=sold_stock.iloc[i]['date'])[0].realized_profit
        profit = account_records.filter(
            code=sold_stock.iloc[i]['code']).filter(
                date=sold_stock.iloc[i]['date'])[0].profit
        realized_profit.append([
            sold_stock.iloc[i]['code'], sold_stock.iloc[i]['date'],
            abs(sold_stock.iloc[i]['amount']),
            round(profit)
        ])

    data = {
        'name': account,
        'data': unrealized_profit,
        'data_date': record_date
    }
    return render(requests, 'account.html', context=data)


def get_month_end_data():
    df_stock_price = queryset2df(StockPriceData.objects.all())
    df_stock_price['month'] = df_stock_price['date'].apply(
        lambda x: datetime.strftime(x, '%Y-%m'))
    df_stock_price['date'] = df_stock_price['date'].apply(
        lambda x: datetime.strftime(x, '%d'))
    df_stock_price = df_stock_price.sort_values(by=['month', 'date'])
    last_month_date_index = []
    for code in df_stock_price['code'].unique():
        df_code = df_stock_price[df_stock_price['code'] == code]
        for month in df_code['month'].unique():
            last_month_date_index.append(
                df_code[df_code['month'] == month].index[-1])
    return df_stock_price.loc[last_month_date_index]


#def show_profits(requests, account):
def show_profits(account):
    transactions = TransactionData.objects.all().filter(account=account)
    df_close_price = get_month_end_data()
    df = queryset2df(transactions).sort_values(by='date')
    df['month'] = df['date'].apply(lambda x: datetime.strftime(x, '%Y-%m'))
    profits = []
    for i in range(len(df_close_price)):
        code = df_close_price['code'].iloc[i]
        month = df_close_price['month'].iloc[i]
        close_price = df_close_price['price'].iloc[i]
        df_code_stock = df[df['code'] == code]
        for j in range(len(df_code_stock)):
            if df_code_stock['month'].iloc[j] <= month:
                cost = df_code_stock['price'].iloc[j] * df_code_stock[
                    'amount'].iloc[j] + df_code_stock['fee'].iloc[j]
                profit = (close_price - df_code_stock['price'].iloc[j]
                          ) * df_code_stock['amount'].iloc[j] * (
                              1 - 0.003 -
                              0.001425) - df_code_stock['fee'].iloc[j]
                profits.append([code, month, round(profit), cost])
    df_profit = pd.DataFrame(profits,
                             columns=['code', 'month', 'profit', 'cost'])
    df_by_month = df_profit[['month', 'profit',
                             'cost']].groupby(by='month').sum()
    return df_by_month
