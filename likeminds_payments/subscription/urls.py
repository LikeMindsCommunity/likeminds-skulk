from django.urls import path
import subscription.plans.view_impl as plan_views
import subscription.subscription_files.subscription_view_impl as views

app_name = "subscription"

urlpatterns = [
    path('create_plan', plan_views.CreatePlanView.as_view(), name="create-plan"),
    path('fetch_plan', plan_views.FetchPlanView.as_view(), name="fetch-plan"),
    path('delete_plan', plan_views.DeletePlanView.as_view(), name="delete-plan"),
    path('create_order', views.CreateOrderView.as_view(), name="create-order"),
    path('verify_order', views.VerifyOrderView.as_view(), name="verify-order"),
    path('create_transaction', views.CreateTransactionView.as_view(), name="create-transaction"),
    path('create_subscription', views.CreateSubscriptionView.as_view(), name="create-subscription"),
    path('start', views.StartSubscriptionView.as_view(), name="start-subscription"),
    path('fetch', views.FetchSubscriptionView.as_view(), name="fetch-subscription"),
    path('fetch_history', views.FetchSubscriptionHistoryView.as_view(), name='fetch-subscription-history'),
    path('fetch_community_meta', views.FetchCommunityMetaView.as_view(), name='fetch-community-meta')
]
