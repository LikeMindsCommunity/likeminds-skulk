from .order_manager import OrderManager
from django.conf import settings

import razorpay.resources.order as order
from .constants import *

import hmac
import hashlib


class OrderImpl(OrderManager):

    order_instance = None
    razorpay_payment_id = None
    razorpay_signature = None

    def __init__(self, order_instance: order = None, razorpay_payment_id: str = None, razorpay_signature: str = None):
        self.order_instance = order_instance
        self.razorpay_payment_id = razorpay_payment_id
        self.razorpay_signature = razorpay_signature

    def get_order_instance(self) -> order:
        return self.order_instance

    def get_razorpay_payment_id(self) -> str:
        return self.razorpay_payment_id

    def get_razorpay_signature(self) -> str:
        return self.razorpay_signature

    def create_order(self) -> dict:

        order_instance = self.get_order_instance()

        if not order_instance:
            return {'error_message': 'error with created order'}

        options = {
            "key": settings.RAZORPAY_KEY,
            "amount": order_instance['amount'],
            "currency": order_instance['currency'],
            "description": ORDER_TEXT,
            "image": LIKEMINDS_LOGO_URL,
            "order_id": order_instance['id'],
            "name": COMPANY_NAME,
            "receipt": "receipt#1",
            "notes": order_instance['notes']
        }

        return options

    def _verify_payment_signature(self):

        message = "{}|{}".format(self.get_order_instance()['id'], self.get_razorpay_payment_id())
        digest = hmac.new(
            key=bytes(settings.RAZORPAY_SECRET, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if digest != self.get_razorpay_signature():
            return {'error_message': 'Signature mismatch'}

        return {'success': True}

    def verify_order(self) -> dict:

        order_instance = self.get_order_instance()

        if not order_instance:
            return {'error_message': 'invalid razorpay_order_id'}

        response = self._verify_payment_signature()

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        return response

    def create_event_order(self) -> dict:

        order_instance = self.get_order_instance()

        if not order_instance:
            return {'success': False, 'error_message': 'error with created order'}

        options = {
            "key": settings.RAZORPAY_KEY,
            "amount": order_instance['amount'],
            "currency": order_instance['currency'],
            "description": ORDER_TEXT,
            "image": LIKEMINDS_LOGO_URL,
            "order_id": order_instance['id'],
            "name": COMPANY_NAME,
            "receipt": "receipt#1",
            "notes": order_instance['notes']
        }

        return options

    def create_community_event_order(self) -> dict:
        order_instance = self.get_order_instance()

        if not order_instance:
            return {'error_message': 'error with created order'}

        options = {
            "key": settings.RAZORPAY_KEY,
            "amount": order_instance['amount'],
            "currency": order_instance['currency'],
            "description": ORDER_TEXT,
            "image": LIKEMINDS_LOGO_URL,
            "order_id": order_instance['id'],
            "name": COMPANY_NAME,
            "notes": order_instance['notes']
        }

        return options
