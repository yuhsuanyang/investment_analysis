from django.db import models


# Create your models here.
class TransactionData(models.Model):
    code = models.CharField(max_length=10, help_text="股票代碼")
    date = models.DateField(help_text="交易日期")
    account = models.CharField(max_length=30, help_text="帳戶")
    price = models.FloatField(help_text="成交價")
    amount = models.IntegerField(help_text="成交量")
    # amount > 0: buy, amount < 0: sell
    fee = models.FloatField(help_text="手續費")

    def __str__(self):
        return f"{self.code} {self.date}"

    @classmethod
    def columns(cls):
        return ['code', 'date', 'account', 'price', 'amount', 'fee']

    def get_values(self):
        return [
            self.code, self.date, self.account, self.price, self.amount,
            self.fee
        ]
