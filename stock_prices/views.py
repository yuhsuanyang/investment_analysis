import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from django.shortcuts import render
from .models import StockPriceData
from transactions.models import TransactionData, RealizedProfit
from accounts.models import Account
from accounts.views import display_unrealized_profit
from utils import queryset2df

# print(transaction_df)

ROOT = Path(__file__).resolve().parent.parent
today = datetime.now().date()


# Create your views here.
def download_stock_price(stock_code, start_date, end_date):
    # dates: yyyy-mm-dd
    stock_code = f"{stock_code}.TW"
    df = yf.download(stock_code, start=start_date, end=end_date)
    return pd.DataFrame({'date': list(df.index), 'close': df['Close'].values})


def update_data(start_date, end_date):
    if (end_date - start_date).days > 1:
        print('updating data...')
        codes = StockPriceData.objects.values('code').distinct()
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
        latest_date = StockPriceData.objects.values('date').order_by(
            '-date').distinct()[0]['date']
        latest_date = latest_date.strftime('%Y-%m-%d')
        print('stock price data is already up-to-date')

    return latest_date


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


def get_total_realized_profit():
    realized_profit_df = queryset2df(RealizedProfit.objects.all())
    if len(realized_profit_df):
        return realized_profit_df.groupby(
            by='account')['profit'].sum().reset_index()
    else:
        return pd.DataFrame([], columns=['account', 'profit'])


def display_stock_condition(requests):
    accounts = {
        acc.name: acc.get_absolute_url()
        for acc in Account.objects.all()
    }
    stocks_all = TransactionData.objects.all()
    print(accounts)
    if not len(accounts):
        return render(requests, 'index.html', context={})

    if not len(stocks_all):
        data = {'account': []}
        for acc in accounts:
            data['account'].append([acc, accounts[acc], 0, 0, 0, 0])
        return render(requests, 'index.html', context=data)

    with open(f"{ROOT}/stock_prices/data_date_record.txt", 'r') as f:
        record_date = f.read().strip()

    record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
    if datetime.now().hour >= 14:  # 14 點以後更新今日收盤價
        end_date = today + timedelta(days=1)
    else:  # 14 點前更新昨日收盤價
        end_date = today
    print(record_date, end_date)
    latest_date = update_data(record_date, end_date)

    transaction_df = queryset2df(stocks_all).sort_values('date').reset_index(
        drop=True)

    initial_stock_price(transaction_df)
    data = {'account': [], 'data_date': latest_date}
    realized_profit = get_total_realized_profit()
    print(realized_profit)
    for acc in accounts:
        #        accounts_data[acc] = transaction_df[transaction_df['account'] == acc]
        _, current_stocks = display_unrealized_profit(acc)
        unrealized_profit = [[
            current_stocks[i][0], current_stocks[i][2], current_stocks[i][6]
        ] for i in range(len(current_stocks))]
        unrealized_profit = pd.DataFrame(unrealized_profit,
                                         columns=['code', 'cost', 'profit'])
        print(unrealized_profit)
        total_value = {}
        total_value['total_investment'] = unrealized_profit['cost'].sum()
        total_value['stock_profit_loss'] = unrealized_profit['profit'].sum()
        if acc in realized_profit['account'].values:
            total_value['realized_profit'] = realized_profit[
                realized_profit['account'] == acc]['profit'].iloc[0]
        else:
            total_value['realized_profit'] = 0

        print(total_value)
        data['account'].append([
            acc, accounts[acc],
            round(total_value['total_investment']),
            round(total_value['stock_profit_loss']) +
            round(total_value['realized_profit']),
            round(total_value['stock_profit_loss']),
            round(total_value['realized_profit'])
        ])


#    print(accounts)
    return render(requests, 'index.html', context=data)
