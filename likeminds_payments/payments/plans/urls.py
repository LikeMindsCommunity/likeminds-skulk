from django.urls import path
from payments.plans.plans_view_impl import CreatePlanView

app_name = "plans"

urlpatterns = [
    path('create/', CreatePlanView.as_view(), name="create_plan")
]
