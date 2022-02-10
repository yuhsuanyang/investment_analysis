from django.db import models


# Create your models here.
class StockPriceData(models.Model):
    code = models.CharField(max_length=10, help_text="股票代碼")
    date = models.DateField(help_text="日期")
    price = models.FloatField(help_text="收盤價")

    def __str__(self):
        return f"{self.code} {self.date}"

    @classmethod
    def columns(cls):
        return ['code', 'date', 'price']

    def get_values(self):
        return [self.code, self.account, self.price]
