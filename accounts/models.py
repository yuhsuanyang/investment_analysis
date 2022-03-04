from django.db import models
from django.urls import reverse


# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=30, help_text="帳戶名稱")
    record_date = models.DateField(help_text="紀錄日期")
    profit = models.FloatField(help_text="損益")
    cost = models.FloatField(help_text="投入成本")

    def __str__(self):
        return f"{self.name} {self.record_date}"

    def get_absolute_url(self):
        print(reverse('account', args=[self.name]))
        return reverse('account', args=[self.name])

#      return f"/account/{self.name}"
