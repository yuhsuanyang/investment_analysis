import pandas as pd
import yfinance as yf
from datetime import datetime
from django.shortcuts import render
from .models import StockPriceData
from transactions.models import TransactionData
from accounts.models import Account
from utils import queryset2df

stocks_all = TransactionData.objects.all()
transaction_df = queryset2df(stocks_all).sort_values('date').reset_index(
    drop=True)


# Create your views here.
def download_stock_price(stock_code, start_date, end_date):
    # dates: yyyy-mm-dd
    stock_code = f"{stock_code}.TW"
    df = yf.download(stock_code, start=start_date, end=end_date)
    return pd.DataFrame({'date': list(df.index), 'close': df['Close'].values})


def initial_stock_price():
    end_date = datetime.now().strftime('%Y-%m-%d')
    codes_t = transaction_df['code'].unique()
    codes_s = StockPriceData.objects.values('code').distinct()

    codes_s = [code['code'] for code in codes_s]

    for code in codes_t:
        if code not in codes_s:
            start_date = transaction_df[transaction_df['code'] == code].iloc[
                0]['date'].strftime('%Y-%m-%d')
            prices = download_stock_price(code, start_date, end_date)
            for i in range(len(prices)):
                stock_price_row = StockPriceData(code=code,
                                                 date=prices['date'][i],
                                                 price=prices['close'][i])
                stock_price_row.save()


def get_account_stocks(acc_name):
    return transaction_df[transaction_df['account'] == acc_name]


def display_stock_condition(requests):
    accounts = Account.objects.values('name').distinct()
    accounts = {acc['name']: {} for acc in accounts}
    for acc in accounts:
        accounts[acc] = get_account_stocks(acc)

    return render(requests, 'index.html', context=accounts)
