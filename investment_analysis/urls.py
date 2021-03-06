"""investment_analysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from transactions.views import buy_transaction_form, sell_transaction_form
from accounts.views import account_form, delete_account, display_stocks
from stock_prices.views import display_stock_condition

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', display_stock_condition, name='index'),
    path('account/<account>/', display_stocks, name='account'),
    path('buy/', buy_transaction_form, name='buy'),
    path('sell/', sell_transaction_form, name='sell'),
    path('new_account/', account_form, name='new_account'),
    path('delete_account/', delete_account, name='delete_account'),
    path(
        'css/styles.css',
        TemplateView.as_view(template_name='styles.css',
                             content_type='text/css'))
]
