from django.db import models


# Create your models here.
class TransactionData(models.Model):
    code = models.CharField(max_length=10, help_text="股票代碼")
    date = models.DateField(help_text="交易日期")
    key = models.CharField(max_length=30,
                           primary_key=True,
                           help_text="code YYYY-MM-DD")
    price = models.FloatField(help_text="成交價")
    amount = models.IntegerField(help_text="成交量")
    fee = models.FloatField(help_text="手續費")

    def __str__(self):
        return f"{self.code} {self.date}"
