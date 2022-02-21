from datetime import datetime
from django.shortcuts import render, redirect
from .models import Account
from transactions.models import TransactionData
from stock_prices.models import StockPriceData


# Create your views here.
def account_form(request):
    data = {}
    if request.method == "POST":
        name = request.POST['acc_name']
        date = datetime.today().date()
        new_account = Account(name=name, record_date=date, profit=0, cost=0)
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
    for code in deleted_codes:
        stock_codes.filter(code=code).delete()
        print(f"{code} delete")

    return render(request, 'delete_account.html', context={'account': name})
