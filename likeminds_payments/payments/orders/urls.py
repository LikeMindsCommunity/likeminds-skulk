from django.urls import path
from payments.orders.orders_view_impl import CreateOrderView, VerifyOrderView

app_name = "orders"

urlpatterns = [
    path('generate/', CreateOrderView.as_view(), name="create_order"),
    path('<str:order_id>/verify/', VerifyOrderView.as_view(), name="verify_order")
]
