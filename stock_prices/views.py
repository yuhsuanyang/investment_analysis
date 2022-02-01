import requests
import pandas as pd
import numpy as np
from io import StringIO
from django.shortcuts import render

# Create your views here.


def convert(x):
    if x == '--':
        return np.nan
    if type(x) == str:
        return float(x.replace(',', ''))
    else:
        return x


def download_stock_price(datestr):  # 下載某天股價
    r = requests.post(
        'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' +
        datestr + '&type=ALL')
    if len(r.text):
        df = pd.read_csv(StringIO(r.text.replace("=", "")),
                         header=["證券代號" in l
                                 for l in r.text.split("\n")].index(True) - 1)
        df = df[['證券代號', '開盤價', '最高價', '最低價', '收盤價', '成交股數', '本益比']]
        df.columns = ['code', 'Open', 'High', 'Low', 'Close', 'Volume', 'PE']
        #        stock_codes = [c.split(' ')[0] for c in stocks]
        #        df = df[df['code'].isin(stock_codes)].reset_index(drop=True)
        converted_df = {'code': df['code']}
        for col in df.columns[1:]:
            converted_df[col] = df[col].apply(convert)
        return pd.DataFrame(converted_df).dropna().reset_index(drop=True)
    else:
        print(datestr, 'no data')
        return
