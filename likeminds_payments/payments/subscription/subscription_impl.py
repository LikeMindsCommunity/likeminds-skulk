from ..subscription.subscription_manager import SubscriptionManager
from ..subscription.constants import subscription_plan_choices, likeminds_logo_url, order_text, company_name, \
    community_api
from ..subscription.serializers import PlanSerializer
from ..utility.plan_utilities import PlanUtilities
from ..utility.api_utilities import ApiUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.time_utilities import TimeUtilities
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper

from ..models import SubscriptionPlan, Transaction, Subscription, SubscriptionHistory
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
        
        if 'description' not in plan_body or not plan_body['description']:
            plan_body['description'] = ''

        if 'referral_free_days' not in plan_body or not plan_body['referral_free_days']:
            plan_body['referral_free_days'] = 0

        if 'image' not in plan_body or not plan_body['image']:
            plan_body['image'] = ''
            # TODO
            # assigning default values according to length of plan
        
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

        if plan_instance.description != plan_body['description']:
            plan_instance.description = plan_body['description']

        if plan_instance.referral_free_days != plan_body['referral_free_days']:
            plan_instance.referral_free_days = plan_body['referral_free_days']

        if plan_instance.image != plan_body['image']:
            plan_instance.image = plan_body['image']

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
    def _get_community_data(community_id: int) -> dict:

        if not community_id:
            return {'error_message': 'send community_id'}

        url = '{url}/{community_id}'.format(url=community_api, community_id=community_id)
        response = ApiUtilities.generate_get_request(url)

        if 'error_message' in response:
            return {'error_message': 'error getting community name'}

        data = {'name': response['community']['name'], 'grace_period': 0}
        if 'grace_period' in response['community']:
            data['grace_period'] = response['community']['grace_period']

        return data

    @staticmethod
    def _create_order_object_data(plan_instance: dict, order_body: dict, community_data: dict) -> dict:

        order_data = {
            "amount": float(plan_instance.cost) * 100,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "plan_id": plan_instance.plan_id,
                "community_name": community_data['name'],
                "name": plan_instance.name,
                "cost": plan_instance.cost,
                "cm_emails": plan_instance.cm_emails,
                "buddy_emails": plan_instance.buddy_emails,
                "payment_page_url": order_body['payment_page_url'],
                "renew": False,
                "grace_period": community_data['grace_period']
            }
        }

        if 'renew' in order_body:
            order_data['notes']['renew'] = order_body['renew']

        if 'user_id' in order_body:
            order_data['notes']['user_id'] = order_body['user_id']

        if 'shared_by' in order_body:
            order_data['notes']['shared_by'] = order_body['shared_by']

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

        community_data = self._get_community_data(plan_instance.community_id)

        if 'error_message' in community_data:
            return {'error_message': community_data['error_message']}

        order_data = self._create_order_object_data(plan_instance, order_body, community_data)
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

    @staticmethod
    def _verify_transaction_signature(payload, signature: str) -> dict:

        message = payload.decode('utf-8')

        digest = hmac.new(
            key=bytes(settings.RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if digest != signature:
            return {'error_message': 'Signature mismatch'}

        return {'success': True}

    @staticmethod
    def _create_transaction_data(transaction_body):
        payment_instance = transaction_body['payload']['payment']['entity']
        refund_instance = {}
        if 'refund' in transaction_body['payload']:
            refund_instance = transaction_body['payload']['refund']['entity']

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.fetch(payment_instance['order_id'])

        if not order_instance:
            return {'error_message': 'no order exists for given payment'}

        order_notes = order_instance['notes']

        transaction_data = {
            "plan_id": order_notes['plan_id'],
            "payment_id": payment_instance['id'],
            "community_name": order_notes['community_name'],
            "plan_name": order_notes['name'],
            "plan_cost": order_notes['cost'],
            "renew": order_notes['renew'],
            "amount": payment_instance['amount'],
            "payment_email": payment_instance['email'],
            "payment_phone": payment_instance['contact'],
            "currency": payment_instance['currency'],
            "is_international": payment_instance['international'],
            "method": payment_instance['method'],
            "status": payment_instance['status'],
            "error_description": "",
            "refund_amount": 0,
            "user_id": None,
            "payment_page_url": order_notes['payment_page_url']
        }

        if payment_instance['error_description'] is not None:
            transaction_data["error_description"] = payment_instance['error_description']

        if 'amount' in refund_instance:
            transaction_data["refund_amount"] = refund_instance['amount']

        if 'user_id' in order_notes:
            transaction_data["user_id"] = order_notes['user_id']

        return transaction_data

    def create_transaction(self, transaction_body: dict, transaction_raw_body, transaction_signature: str) -> dict:

        # TODO
        # signature_verification = self._verify_transaction_signature(transaction_raw_body, transaction_signature)
        #
        # if 'error_message' in signature_verification:
        #     return {'error_message': signature_verification['error_message']}

        existing_transaction_instance = Transaction.get_transaction_or_None(
            transaction_body['payload']['payment']['entity']['id']
        )

        if existing_transaction_instance:

            if transaction_body["event"] == "refund.processed":
                existing_transaction_instance.status = "refund"
                existing_transaction_instance.save()

                return {'success': True}
            else:
                return {'error_message': 'transaction exists with given plan_id'}

        transaction_data = self._create_transaction_data(transaction_body)

        if 'error_message' in transaction_data:
            return {'error_message': transaction_data['error_message']}

        transaction_instance = Transaction.create_instance(transaction_data)

        if not transaction_instance:
            return {'error_message': 'error while creating transaction'}

        return {'success': True}

    def update_transaction(self, payment_id: str, user_id: str) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=payment_id)

        if not transaction_instance:
            return {'error_message': 'no transaction exists with given payment_id'}

        user_id_int = NumberUtilities.get_integer_from_string(user_id)

        if user_id_int == 0:
            return {'error_message': 'invalid user_id'}

        if transaction_instance.user_id is not None and transaction_instance.user_id != user_id_int:
            return {'error_message': 'invalid user'}

        if transaction_instance.user_id is not None and transaction_instance.user_id == user_id_int:
            return {'message': 'user already updated'}

        transaction_instance.user_id = user_id_int
        transaction_instance.save()

        return {'success': True}

    @staticmethod
    def _generate_data_for_new_subscription(transaction_instance: dict, subscription_plan_instance: dict) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        data = {
            "subscription_data": {
                "user_id": transaction_instance.user_id,
                "community_id": subscription_plan_instance.community_id,
                "plan_id": subscription_plan_instance.plan_id,
                "date_subscribed": current_time,
                "trial_end": None,
                "valid_till": TimeUtilities.add_months_in_epoch_time(current_time,
                                                                     subscription_plan_instance.duration_in_months),
                "type": "onetime"
            }
        }

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": '',
            "transaction": transaction_instance,
            "type": "paid",
            "status": "paid"
        }

        return data

    @staticmethod
    def _generate_data_for_existing_subscription(subscription_instance: dict,
                                                 subscription_plan_instance: dict,
                                                 transaction_instance: dict) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        data = {
            "subscription_data": {
                "type": "onetime"
            }
        }

        existing_valid_till = subscription_instance.valid_till
        if existing_valid_till >= current_time:
            data["subscription_data"]["valid_till"] = TimeUtilities.add_months_in_epoch_time(
                existing_valid_till,
                subscription_plan_instance.duration_in_months)
        else:
            data["subscription_data"]["valid_till"] = TimeUtilities.add_months_in_epoch_time(
                current_time,
                subscription_plan_instance.duration_in_months)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": '',
            "transaction": transaction_instance,
            "type": "paid",
            "status": "paid"
        }

        return data

    def create_subscription(self, payment_id: str) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=payment_id)

        if not transaction_instance:
            return {'error_message': 'no transaction exists for given payment_id'}

        subscription_plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if not subscription_plan_instance:
            return {'error_message': 'error getting plan details for specified transaction'}

        if not transaction_instance.renew:

            data = self._generate_data_for_new_subscription(transaction_instance, subscription_plan_instance)

            subscription_instance = Subscription.create_instance(data['subscription_data'])
            subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

            if not subscription_instance:
                return {'error_message': 'error creating subscription'}

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        else:

            subscription_instance = Subscription.get_subscription_or_None(
                transaction_instance['user_id'], transaction_instance['community_id']
            )

            if not subscription_instance:
                return {'error_message': 'error renewing subscription'}

            data = self._generate_data_for_existing_subscription(subscription_instance,
                                                                 subscription_plan_instance,
                                                                 transaction_instance)

            subscription_instance.type = data["subscription_data"]["type"]
            subscription_instance.valid_till = data["subscription_data"]["valid_till"]
            subscription_instance.save()

            subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

            if not subscription_instance:
                return {'error_message': 'error updating subscription'}

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}
