import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from django.shortcuts import render
from .models import StockPriceData
from transactions.models import TransactionData
from accounts.models import Account
from utils import queryset2df

# print(transaction_df)

ROOT = Path(__file__).resolve().parent.parent
today = datetime.now().date()  #.strftime('%Y-%m-%d')


# Create your views here.
def download_stock_price(stock_code, start_date, end_date):
    # dates: yyyy-mm-dd
    stock_code = f"{stock_code}.TW"
    df = yf.download(stock_code, start=start_date, end=end_date)
    return pd.DataFrame({'date': list(df.index), 'close': df['Close'].values})


def update_data():
    with open(f"{ROOT}/stock_prices/data_date_record.txt", 'r') as f:
        record_date = f.read().strip()
    print(record_date)
    record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
    if record_date < today:
        print('updating data...')
        codes = StockPriceData.objects.values('code').distinct()
        start_date = (record_date + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        for code in codes:
            prices = download_stock_price(code['code'], start_date, end_date)
            for i in range(len(prices)):
                stock_price_row = StockPriceData(code=code['code'],
                                                 date=prices['date'][i],
                                                 price=prices['close'][i])
                stock_price_row.save()
        latest_date = StockPriceData.objects.values('date').order_by(
            '-date').distinct()[0]['date']
        latest_date = latest_date.strftime('%Y-%m-%d')
        with open(f"{ROOT}/stock_prices/data_date_record.txt", 'w') as f:
            f.write(latest_date)

    else:
        print('stock price data is already up-to-date')

    return


def initial_stock_price(df):
    end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    codes_t = df['code'].unique()
    codes_s = StockPriceData.objects.values('code').distinct()

    codes_s = [code['code'] for code in codes_s]

    for code in codes_t:
        if code not in codes_s:
            start_date = df[df['code'] == code].iloc[0]['date'].strftime(
                '%Y-%m-%d')
            prices = download_stock_price(code, start_date, end_date)
            for i in range(len(prices)):
                stock_price_row = StockPriceData(code=code,
                                                 date=prices['date'][i],
                                                 price=prices['close'][i])
                stock_price_row.save()


def get_account_overview(df):
    data = {}
    data['total_investment'] = (df['amount'] * df['price'] + df['fee']).sum()
    data['stock_profit_loss'] = (
        (df['latest_price'] - df['price']) * df['amount'] - df['fee'] -
        df['sell_cost']).sum()
    return data


def display_stock_condition(requests):
    if datetime.now().hour >= 14:  # update close prices after 14
        update_data()

    stocks_all = TransactionData.objects.all()
    transaction_df = queryset2df(stocks_all).sort_values('date').reset_index(
        drop=True)

    initial_stock_price(transaction_df)
    all_prices = StockPriceData.objects.all().order_by('-date')
    latest_price = []
    for i in range(len(transaction_df)):
        price = all_prices.filter(code=transaction_df['code'][i])[0]
        #        print(price)
        latest_price.append([price.date, round(price.price, 2)])
    transaction_df[['today', 'latest_price']] = pd.DataFrame(latest_price)
    transaction_df['sell_cost'] = transaction_df[
        'latest_price'] * transaction_df['amount'] * (
            0.003 + 0.001425)  # 0.003: 證交稅 0.001425: 賣出手續費
    transaction_df['sell_cost'] = round(transaction_df['sell_cost'])
    print(transaction_df[[
        'code', 'account', 'date', 'price', 'latest_price', 'today'
    ]])

    accounts = Account.objects.values('name').distinct()
    accounts = {acc['name']: {} for acc in accounts}
    data = {'account': []}
    for acc in accounts:
        accounts[acc] = transaction_df[transaction_df['account'] == acc]
        total_value = get_account_overview(accounts[acc])
        data['account'].append([
            acc,
            round(total_value['total_investment']),
            round(total_value['stock_profit_loss'])
        ])


#    print(accounts)
    return render(requests, 'index.html', context=data)
