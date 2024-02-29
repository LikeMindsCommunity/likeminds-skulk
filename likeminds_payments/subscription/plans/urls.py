from django.urls import path
from .plan_view_impl import *

app_name = "plans"

urlpatterns = [
    path('billing/<int:community_id>', BillingPlanView.as_view(), name="community_billing_plan"),
    path('tiers/',TierPlanView.as_view(), name="tier_plan")
]

