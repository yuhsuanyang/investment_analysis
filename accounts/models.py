from django.db import models
from django.urls import reverse


# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=30, help_text="帳戶名稱")
    record_date = models.DateField(help_text="紀錄日期")
    realized_profit = models.FloatField(help_text="已實現損益")

    #    unrealized_profit = models.FloatField(help_text="未實現損益")
    #    cost = models.FloatField(help_text="投入成本")

    def __str__(self):
        return f"{self.name} {self.record_date}"

    def get_absolute_url(self):
        print(reverse('account', args=[self.name]))
        return reverse('account', args=[self.name])


#    return f"/account/{self.name}"
