from django.urls import path
from .transaction_view_impl import *

app_name = "transactions"

urlpatterns = [
    path('fetch_settlement_amount', FetchSettlementAmountView.as_view(), name="fetch-settlement-amount"),
]
