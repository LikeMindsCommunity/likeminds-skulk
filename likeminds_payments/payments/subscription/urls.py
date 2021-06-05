from django.urls import path
from ..subscription.subscription_view_impl import CreatePlanView, FetchPlanView, DeletePlanView, CreateOrderView, \
    VerifyOrderView, CreateTransactionView, UpdateTransactionView, CreateSubscriptionView

app_name = "subscription"

urlpatterns = [
    path('create_plan/', CreatePlanView.as_view(), name="create-plan"),
    path('fetch_plan/', FetchPlanView.as_view(), name="fetch-plan"),
    path('delete_plan/', DeletePlanView.as_view(), name="delete-plan"),
    path('create_order/', CreateOrderView.as_view(), name="create-order"),
    path('verify_order/', VerifyOrderView.as_view(), name="verify-order"),
    path('create_transaction/', CreateTransactionView.as_view(), name="create-transaction"),
    path('update_transaction/', UpdateTransactionView.as_view(), name="update-transaction"),
    path('create_subscription/', CreateSubscriptionView.as_view(), name="create-subscription")
]
