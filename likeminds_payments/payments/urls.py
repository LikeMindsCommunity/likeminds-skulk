from django.urls import path, include

app_name = "payments"

urlpatterns = [
    path('', include('payments.plans.urls'), name='plans'),
    path('orders/', include('payments.orders.urls'), name='orders'),
]