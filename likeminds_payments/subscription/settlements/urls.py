from django.urls import path
from .settlement_view_impl import *

app_name = "settlements"

urlpatterns = [
    path('initiate', InitiateSettlementView.as_view(), name="initiate-settlement"),
    path('create', CreateSettlementView.as_view(), name="create-settlement"),
    path('fetch', FetchSettlementView.as_view(), name="fetch-settlement")
]
