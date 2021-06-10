from django.urls import path, include

app_name = "payments"

urlpatterns = [
    path('subscription/', include('payments.subscription.urls'), name='subscription'),
    path('gd/', include('payments.growth_dashboard.urls'), name='gd'),
]
