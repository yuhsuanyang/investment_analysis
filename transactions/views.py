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


def cal_profit(sell_price, buy_price, amount, fee):
    return amount * (sell_price - buy_price) * (1 - 0.003) - fee


def cal_realized_profit(df_transaction, sell_price, total_sell_amount,
                        sell_fee):
    profit = 0
    for i in range(len(df_transaction)):
        stock_amount = df_transaction.iloc[i]['amount']
        buy_price = df_transaction.iloc[i]['price']
        buy_fee = df_transaction.iloc[i]['fee']
        if stock_amount >= total_sell_amount:
            profit += cal_profit(sell_price, buy_price, total_sell_amount,
                                 buy_fee * (total_sell_amount / stock_amount))
            total_sell_amount = max(0, total_sell_amount - stock_amount)
            break
        else:
            profit += cal_profit(sell_price, buy_price, stock_amount, buy_fee)
            total_sell_amount -= stock_amount
    return profit - sell_fee


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
        stock_code = request.POST['stock_code'].split(' ')[0]
        date = request.POST['date']
        account = request.POST['account']
        stock_price = request.POST['stock_price']
        stock_amount = request.POST['stock_amount']
        #        stock_amount1 = request.POST['stock_amount']
        fee = request.POST['fee']

        transaction_records = TransactionData.objects.all().filter(
            account=account).filter(code=stock_code)
        print(stock_code, account)
        transaction_record_df = queryset2df(transaction_records)
        print(transaction_record_df)
        if not len(transaction_records) or transaction_record_df['amount'].sum(
        ) < int(stock_amount):  # 庫存量不足
            return render(request,
                          'warning.html',
                          context={'message': f'{stock_code}庫存量不足！'})

        profit = cal_realized_profit(transaction_record_df, float(stock_price),
                                     int(stock_amount), int(fee))
        realized_profit = Account(
            name=account,
            record_date=date,
            realized_profit=profit,
        )
        realized_profit.save()

        transaction = TransactionData(code=stock_code.split(' ')[0],
                                      date=date,
                                      account=account,
                                      price=stock_price,
                                      amount=(-1) * int(stock_amount),
                                      fee=fee)
        transaction.save()


#        transaction_records = TransactionData.objects.all().filter(
#            account=account).filter(code=stock_code)
#        transaction_df = queryset2df(transaction_records)

#        if not transaction_df['amount'].sum():  # 全部賣出 加到已實現損益
#            transaction_records.delete()

#            print(f'{stock_code} sold out')

    data = {
        'accounts': accounts,
        'stock_codes': stock_codes['code'].tolist(),
        'color': 'lime'
    }
    return render(request, 'new_transaction.html', context=data)
