from datetime import datetime
from django.shortcuts import render, redirect
from .models import Account


# Create your views here.
def account_form(request):
    data = {}
    if request.method == "POST":
        name = request.POST['acc_name']
        date = datetime.today().date()
        new_account = Account(name=name, record_date=date, profit=0, cost=0)
        new_account.save()
        print(f"account {name} created!")
        return redirect('/new_account')
    return render(request, 'new_account.html', context=data)
