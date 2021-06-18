from django.urls import path
from .plans.view_impl import *
from .orders.view_impl import *
from .transactions.view_impl import *
from .subscriptions.view_impl import *
from .subscription_histories.view_impl import *

app_name = "subscription"

urlpatterns = [
    path('create_plan', CreatePlanView.as_view(), name="create-plan"),
    path('fetch_plan', FetchPlanView.as_view(), name="fetch-plan"),
    path('delete_plan', DeletePlanView.as_view(), name="delete-plan"),
    path('create_order', CreateOrderView.as_view(), name="create-order"),
    path('verify_order', VerifyOrderView.as_view(), name="verify-order"),
    path('create_transaction', CreateTransactionView.as_view(), name="create-transaction"),
    path('create_subscription', CreateSubscriptionView.as_view(), name="create-subscription"),
    path('start', StartSubscriptionView.as_view(), name="start-subscription"),
    path('fetch', FetchSubscriptionView.as_view(), name="fetch-subscription"),
    path('fetch_history', FetchSubscriptionHistoryView.as_view(), name='fetch-subscription-history'),
    path('fetch_community_meta', FetchCommunityMetaView.as_view(), name='fetch-community-meta')
]
