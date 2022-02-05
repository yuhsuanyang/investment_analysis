from django import forms
from .models import TransactionData


class TransactionModelForm(forms.ModelForm):
    class Meta:
        model = TransactionData
        fields = ['code', 'date', 'price', 'amount', 'fee']

        labels = {
            'code': '股票代碼',
            'date': '交易日期',
            'price': '交易價格',
            'amount': '交易量',
            'fee': '手續費'
        }
