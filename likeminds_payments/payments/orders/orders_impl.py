from ..orders.orders_manager import OrdersManager
from ..models import Plans
from django.conf import settings
import hmac
import hashlib
import razorpay

RAZORPAY_CLIENT = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

class OrdersImpl(OrdersManager):

    def create_order_object_for_razorpay(self, plan_instance, plans_count) -> dict:
        order_data = {
            "amount": float(plan_instance.plan_cost)*100,
            "currency": "INR",
            "receipt": "receipt#"+str(plans_count),
            "notes": {
                "community name": plan_instance.community_name,
                "community id": plan_instance.community_id,
                "plan name": plan_instance.plan_name,
                "plan cost": plan_instance.plan_cost,
                "plan length": plan_instance.plan_length,
                "community join link": plan_instance.community_join_link,
                "cm email": plan_instance.community_manager_mail,
                "cb email": plan_instance.community_buddy_mail
            }
        }

        return order_data


    def call_razorpay_api_to_create_object(self, order_data) -> dict:
        order = RAZORPAY_CLIENT.order.create(data=order_data)

        if not order:
            return {'error_message': 'Error creating order'}
        
        razorpay_client_options = {
            "key": "rzp_test_3wlhDTEXICbHji",
            "order_id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "name": "Likeminds Pvt. Ltd.",
            "description": "Order Payment",
            "image": "https://uploads-ssl.webflow.com/605033ad58253a624fdb1964/6055d9b3d5d4c689c60acac7_Favicon%20256X256.jpg",
            "notes": order['notes']
        }

        return razorpay_client_options


    def create_order(self, plan_id:str) -> dict:
        plan_instance = Plans.get_plan_or_None(plan_id)
        plans_count = Plans.get_plan_size()

        if not plan_instance:
            return {'error_message': 'No plan found with given planId'}
        
        order_data = self.create_order_object_for_razorpay(plan_instance, plans_count)
        client_options = self.call_razorpay_api_to_create_object(order_data)

        if not client_options:
            return {'error_message': 'Error creating client options'}
        
        return client_options


    def verify_order(self, req_body:dict) -> dict:
        order_instance = RAZORPAY_CLIENT.order.fetch(req_body['razorpay_order_id'])

        if not order_instance:
            return {'error_message': 'error getting order object'}

        message = "{}|{}".format(req_body['razorpay_order_id'], req_body['razorpay_payment_id'])
        digest = hmac.new(
            key=bytes(os.getenv('RAZORPAY_SECRET'), 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if (digest != req_body['razorpay_signature']):
            return {'error_message': 'Signature mismatch'}
        
        return {'redirect_url': order_instance['notes']['community join link']}
        
