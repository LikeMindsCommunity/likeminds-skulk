from django.urls import path
import subscription.subscription_files.subscription_view_impl as views

app_name = "subscription"

urlpatterns = [
    path('create_plan/', views.CreatePlanView.as_view(), name="create-plan"),
    path('fetch_plan/', views.FetchPlanView.as_view(), name="fetch-plan"),
    path('delete_plan/', views.DeletePlanView.as_view(), name="delete-plan"),
    path('create_order/', views.CreateOrderView.as_view(), name="create-order"),
    path('verify_order/', views.VerifyOrderView.as_view(), name="verify-order"),
    path('create_transaction/', views.CreateTransactionView.as_view(), name="create-transaction"),
    path('fetch_transactions/', views.FetchTransactionsView.as_view(), name="fetch-transactions"),
    path('refund_transaction/', views.RefundTransactionView.as_view(), name="refund-transaction"),
    path('create_subscription/', views.CreateSubscriptionView.as_view(), name="create-subscription"),
    path('start/', views.StartSubscriptionView.as_view(), name="start-subscription"),
    path('fetch/', views.FetchSubscriptionView.as_view(), name="fetch-subscription"),
    path('cancel/', views.CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path('fetch_history/', views.FetchSubscriptionHistoryView.as_view(), name='fetch-subscription-history'),
    path('fetch_community_meta/', views.FetchCommunityMetaView.as_view(), name='fetch-community-meta')
]
