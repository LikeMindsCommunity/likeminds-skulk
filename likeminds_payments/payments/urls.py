from django.urls import path, include

app_name = "payments"

urlpatterns = [
    path('plans/', include('payments.plans.urls'), name='plans'),
    path('orders/', include('payments.orders.urls'), name='orders'),
    path('subscription/', include('payments.subscription.urls'), name='subscription'),
    path('gd/', include('payments.growth_dashboard.urls'), name='gd'),
]
