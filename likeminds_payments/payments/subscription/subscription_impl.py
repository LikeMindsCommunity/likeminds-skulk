from ..subscription.subscription_manager import SubscriptionManager
from ..subscription.constants import subscription_plan_choices, likeminds_logo_url, order_text, company_name, community_api
from ..subscription.serializers import PlanSerializer
from ..utility.plan_utilities import PlanUtilities
from ..utility.api_utilities import ApiUtilities
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper

from ..models import SubscriptionPlan
from django.conf import settings

import hmac
import hashlib


class SubscriptionImpl(SubscriptionManager):

    @staticmethod
    def _create_new_plan_object(plan_body: dict) -> dict:

        if 'name' not in plan_body or not plan_body['name']:
            plan_body['name'] = ""
        
        if plan_body['duration_name'] in subscription_plan_choices:
            plan_body['duration_in_months'] = subscription_plan_choices[plan_body['duration_name']]
        
        if 'trials' not in plan_body or not plan_body['trials']:
            plan_body['trials'] = 0
        
        return plan_body

    @staticmethod
    def _update_existing_plan_object(plan_body: dict, plan_instance: dict) -> dict:

        if plan_instance.name != plan_body['name']:
            plan_instance.name = plan_body['name']

        if plan_instance.cost != plan_body['cost']:
            plan_instance.cost = plan_body['cost']

        if plan_instance.cm_emails != plan_body['cm_emails']:
            plan_instance.cm_emails = plan_body['cm_emails']

        if plan_instance.buddy_emails != plan_body['buddy_emails']:
            plan_instance.buddy_emails = plan_body['buddy_emails']

        return plan_instance

    @staticmethod
    def _generate_response_from_plan(plan_instance: dict) -> dict:

        if not plan_instance.plan_id:
            return {'error_message': 'issue with created plan object'}

        return {'url': PlanUtilities.generate_plan_url(plan_instance.plan_id)}

    def create_plan(self, plan_body: dict) -> dict:

        if 'plan_id' not in plan_body or not plan_body['plan_id']:
            
            plan_instance_body = self._create_new_plan_object(plan_body)
            plan_instance = SubscriptionPlan.create_instance(plan_instance_body)

            if not plan_instance:
                return {'error_message': 'error creating plan'}

            response = self._generate_response_from_plan(plan_instance)

            return response

        else:

            plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=plan_body['plan_id'])

            if not plan_instance:
                return {'error_message': 'invalid plan_id'}

            plan_updated_instance = self._update_existing_plan_object(plan_body, plan_instance)
            plan_updated_instance.save()

            response = self._generate_response_from_plan(plan_updated_instance)

            return response

    @staticmethod
    def _fetch_plans(community_id):
        return SubscriptionPlan.objects.filter(community_id=community_id).order_by('created_at')

    @staticmethod
    def _serialize_plans(plans):
        return PlanSerializer(plans)

    def fetch_plan(self, community_id: str) -> object:

        plans = self._fetch_plans(community_id)

        if len(plans) == 0:
            return {'error_message': 'no plans exist with provided community_id'}

        return self._serialize_plans(plans)

    @staticmethod
    def _delete_plan_instance(plan_instance: dict) -> dict:

        if not plan_instance.is_deleted:
            plan_instance.is_deleted = True

        return plan_instance

    def delete_plan(self, plan_id: str) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=plan_id)

        if not plan_instance:
            return {'error_message': 'invalid plan_id'}

        plan_deleted_instance = self._delete_plan_instance(plan_instance)
        plan_deleted_instance.save()

        return {'success': True}

    @staticmethod
    def _get_community_name(community_id: int) -> dict:

        if not community_id:
            return {'error_message': 'send community_id'}

        url = '{url}/{community_id}'.format(url=community_api, community_id=community_id)
        response = ApiUtilities.generate_get_request(url)

        if 'error_message' in response:
            return {'error_message': 'error getting community name'}

        return {'value': response['community']['name']}

    @staticmethod
    def _create_order_object_data(plan_instance: dict, order_body: dict, community_name: str) -> dict:

        order_data = {
            "amount": float(plan_instance.cost) * 100,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "plan_id": plan_instance.plan_id,
                "community_name": community_name,
                "name": plan_instance.name,
                "cost": plan_instance.cost,
                "cm_emails": plan_instance.cm_emails,
                "buddy_emails": plan_instance.buddy_emails,
                "payment_page_url": order_body['payment_page_url'],
                "renew": False
            }
        }

        if 'renew' in order_body:
            order_data['notes']['renew'] = order_body['renew']

        return order_data

    @staticmethod
    def _create_razorpay_client_options(order_data: dict) -> dict:

        razorpay_client = RazorpayWrapper.get_instance()

        order = razorpay_client.order.create(data=order_data)

        if not order:
            return {'error_message': 'error while creating order'}

        options = {
            "key": settings.RAZORPAY_KEY,
            "amount": order['amount'],
            "currency": order['currency'],
            "description": order_text,
            "image": likeminds_logo_url,
            "order_id": order['id'],
            "name": company_name,
            "receipt": "receipt#1",
            "notes": order['notes']
        }

        return options

    def create_order(self, order_body: dict) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(order_body['plan_id'])

        if not plan_instance:
            return {'error_message': 'invalid plan_id'}

        if plan_instance.is_deleted:
            return {'error_message': 'plan no longer exists'}

        community_name = self._get_community_name(plan_instance.community_id)

        if 'error_message' in community_name:
            return {'error_message': community_name['error_message']}

        order_data = self._create_order_object_data(plan_instance, order_body, community_name['value'])
        options = self._create_razorpay_client_options(order_data)

        if 'error_message' in options:
            return {'error_message': options['error_message']}

        return options

    @staticmethod
    def _verify_payment_signature(payment_body):

        message = "{}|{}".format(payment_body['razorpay_order_id'], payment_body['razorpay_payment_id'])
        digest = hmac.new(
            key=bytes(settings.RAZORPAY_SECRET, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if digest != payment_body['razorpay_signature']:
            return {'error_message': 'Signature mismatch'}

        return {'success': True}

    def verify_order(self, payment_body: dict) -> dict:

        if payment_body['razorpay_order_id'] != payment_body['order_id']:
            return {'error_message': 'order_id not matching with razorpay_order_id'}

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.fetch(payment_body['order_id'])

        if not order_instance:
            return {'error_message': 'invalid razorpay_order_id'}

        response = self._verify_payment_signature(payment_body)

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        return response

    def create_transaction(self, transaction_body: dict) -> dict:
        pass

    def update_transaction(self, payment_id: str) -> dict:
        pass

    def create_subscription(self, payment_id: str) -> dict:
        pass
