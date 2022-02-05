from django.shortcuts import render, redirect
from accounts.models import Account
from .forms import TransactionModelForm


# Create your views here.
def main(request):
    data = {'message': 'hi'}
    return render(request, 'index.html', context=data)


def transaction_form(request):
    accounts = [acc.name for acc in Account.objects.all()]
    if not len(accounts):
        return render(request, 'warning_no_account.html', context={})
    form = TransactionModelForm()
    if request.method == "POST":
        form = TransactionModelForm(request.POST)
        print(form)
        #        if form.is_valid():
        #            form.save()
        return redirect('/new_transaction')

    data = {'form': form, 'accounts': accounts}
    print(data['accounts'])
    return render(request, 'new_transaction.html', context=data)
