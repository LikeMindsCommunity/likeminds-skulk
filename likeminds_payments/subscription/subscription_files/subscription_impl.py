from ..subscription_files.subscription_manager import SubscriptionManager
from ..subscription_files.constants import subscription_plan_choices, likeminds_logo_url, order_text, company_name, \
    community_api, lifetime_valid_till, member_state_api, community_questions_api, notify_period
from ..subscription_files.serializers import PlanSerializer, SubscriptionSerializer, SubscriptionHistorySerializer
from ..utility.plan_utilities import PlanUtilities
from ..utility.api_utilities import ApiUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.time_utilities import TimeUtilities
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper

from ..models import SubscriptionPlan, Transaction, Subscription, SubscriptionHistory
from django.conf import settings

import hmac
import hashlib
import json


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

        message = json.dumps(payload)

        razorpay_client = RazorpayWrapper.get_instance()

        digest = razorpay_client.utility.verify_webhook_signature(
            message, signature, settings.RAZORPAY_WEBHOOK_SECRET)

        # digest = hmac.new(
        #     key=bytes(settings.RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
        #     msg=bytes(message, 'utf-8'),
        #     digestmod=hashlib.sha256
        # ).hexdigest()

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
            "payment_page_url": order_notes['payment_page_url'],
            "shared_by": None,
            "grace_period": 0
        }

        if payment_instance['error_description'] is not None:
            transaction_data["error_description"] = payment_instance['error_description']

        if 'amount' in refund_instance:
            transaction_data['refund_amount'] = refund_instance['amount']

        if 'user_id' in order_notes:
            transaction_data['user_id'] = order_notes['user_id']

        if 'shared_by' in order_notes:
            transaction_data['shared_by'] = order_notes['shared_by']

        if 'grace_period' in order_notes:
            transaction_data['grace_period'] = order_notes['grace_period']

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

                if existing_transaction_instance.user_id is not None:
                    subscription_instance = Subscription.get_subscription_or_None(
                        existing_transaction_instance.user_id, existing_transaction_instance.community_id)

                    if subscription_instance is not None:
                        current_time = TimeUtilities.current_time_in_milliseconds()
                        subscription_instance.valid_till = TimeUtilities.subtract_days_in_epoch_time(current_time, 1)
                        subscription_instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(
                            subscription_instance.valid_till, notify_period)
                        subscription_instance.save()

                    subscription_history_instance = SubscriptionHistory.objects.get(
                        transaction=existing_transaction_instance)

                    if subscription_history_instance is not None:
                        subscription_history_instance.type = 'refunded'
                        subscription_history_instance.save()

                return {'success': True}
            else:
                return {'error_message': 'transaction exists with given plan_id'}

        transaction_data = self._create_transaction_data(transaction_body)

        if 'error_message' in transaction_data:
            return {'error_message': transaction_data['error_message']}

        transaction_instance = Transaction.create_instance(transaction_data)

        if not transaction_instance:
            return {'error_message': 'error while creating transaction'}

        if transaction_body['event'] == 'captured':
            if transaction_data['renew'] and transaction_data['user_id'] is not None:
                data = {
                    'payment_id': transaction_data['payment_id']
                }
                create_subscription = self.create_subscription(data, transaction_data['user_id'])

                if 'error_message' in create_subscription:
                    return {'error_message': create_subscription['error_message']}

        return {'success': True}

    @staticmethod
    def _check_if_transaction_is_used(payment_id: str) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=payment_id)

        if transaction_instance is None:
            return {'error_message': 'no transaction exists for given payment_id'}

        if Subscription.objects.filter(transaction=transaction_instance).exists():
            return {'abort_execution': 'special case'}

        if SubscriptionHistory.objects.filter(transaction=transaction_instance).exists():
            return {'abort_execution': 'special case'}

        return {'transaction': transaction_instance}

    @staticmethod
    def _generate_data_for_new_subscription_against_transaction(transaction_instance: dict,
                                                                subscription_plan_instance: dict,
                                                                user_id: int) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        data = {
            "subscription_data": {
                "user_id": transaction_instance.user_id,
                "community_id": subscription_plan_instance.community_id,
                "plan_id": subscription_plan_instance.plan_id,
                "date_subscribed": current_time,
                "valid_till": TimeUtilities.add_months_in_epoch_time(current_time,
                                                                     subscription_plan_instance.duration_in_months),
                "type": "onetime",
                "transaction": transaction_instance,
            }
        }

        if subscription_plan_instance.duration_in_months == subscription_plan_choices["lifetime"]:
            data["subscription_data"]["type"] = "lifetime"
            data["subscription_data"]["valid_till"] = lifetime_valid_till

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], notify_period)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": 'onetime payment',
            "transaction": transaction_instance,
            "type": "paid",
            "user_id": user_id,
            "community_id": subscription_plan_instance.community_id
        }

        if subscription_plan_instance.duration_in_months == subscription_plan_choices["lifetime"]:
            data["subscription_history_data"]["description"] = "lifetime payment"

        return data

    @staticmethod
    def _generate_data_for_existing_subscription_against_transaction(subscription_instance: dict,
                                                                     subscription_plan_instance: dict,
                                                                     transaction_instance: dict) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        data = {
            "subscription_data": {
                "type": "onetime",
                "valid_till": 0
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

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], notify_period)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": 'renewal payment',
            "transaction": transaction_instance,
            "type": "paid",
            "user_id": subscription_instance.user_id,
            "community_id": subscription_instance.community_id
        }

        if existing_valid_till >= current_time:
            data["subscription_history_data"]["start_date"] = existing_valid_till

        return data

    @staticmethod
    def _generate_data_for_existing_subscription_against_referral(subscription_instance: dict,
                                                                  subscription_plan_instance: dict,
                                                                  transaction_instance: dict) -> dict:
        current_time = TimeUtilities.current_time_in_milliseconds()
        existing_valid_till = subscription_instance.valid_till

        data = {
            "subscription_data": {
                "valid_till": TimeUtilities.subtract_days_in_epoch_time(TimeUtilities.add_days_in_epoch_time(
                    existing_valid_till, subscription_plan_instance.referral_free_days), 1)
            }
        }

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], notify_period)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": 'renewal payment',
            "transaction": transaction_instance,
            "type": "referral",
            "user_id": subscription_instance.user_id,
            "community_id": subscription_instance.community_id
        }

        if existing_valid_till >= current_time:
            data["subscription_history_data"]["start_date"] = existing_valid_till

        return data

    @staticmethod
    def _generate_subscription_against_transaction(transaction_instance: dict, user_id: int) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'no plan exist for this transaction, contact your cm.'}

        if not transaction_instance.renew:
            if transaction_instance.user_id is None:
                transaction_instance.user_id = user_id
                transaction_instance.save()

                data = SubscriptionImpl._generate_data_for_new_subscription_against_transaction(
                    transaction_instance, plan_instance, user_id)

                subscription_instance = Subscription.create_instance(data['subscription_data'])
                subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

                if transaction_instance.shared_by is not None:
                    referrer_subscription_instance = Subscription.get_subscription_or_None(
                        transaction_instance.shared_by, transaction_instance.community_id
                    )

                    if referrer_subscription_instance.type != 'onetime':
                        return {'error_message': 'referrer user is not having onetime subscription'}

                    referrer_data = SubscriptionImpl._generate_data_for_existing_subscription_against_referral(
                        referrer_subscription_instance, plan_instance, transaction_instance)

                    referrer_subscription_instance.type = referrer_data["subscription_data"]["type"]
                    referrer_subscription_instance.valid_till = referrer_data["subscription_data"]["valid_till"]
                    referrer_subscription_instance.renewal_due = referrer_data["subscription_data"]["renewal_due"]
                    referrer_subscription_instance.save()

                    referrer_subscription_history_instance = SubscriptionHistory.create_instance(
                        referrer_data['subscription_history_data'])

                    if not referrer_subscription_history_instance:
                        return {'error_message': 'error creating subscription history for referrer user'}

                if not subscription_instance:
                    return {'error_message': 'error creating subscription'}

                if not subscription_history_instance:
                    return {'error_message': 'error creating subscription history'}

                return {'success': True}

            return {'error_message': 'Payment ID already used'}

        if transaction_instance.renew:
            if transaction_instance.user_id is None:
                return {'error_message': "user ID doesn't exist for renewal transaction"}

            if transaction_instance.user_id != user_id:
                return {'error_message': 'Invalid user ID'}

            subscription_instance = Subscription.get_subscription_or_None(
                transaction_instance.user_id, transaction_instance.community_id
            )

            if not subscription_instance:
                return {'error_message': 'no subscription exists for given user in given community'}

            if subscription_instance.type == 'lifetime':
                return {'error_message': 'cannot renew a lifetime subscription'}

            data = SubscriptionImpl._generate_data_for_existing_subscription_against_transaction(
                subscription_instance, plan_instance, transaction_instance)

            subscription_instance.type = data["subscription_data"]["type"]
            subscription_instance.valid_till = data["subscription_data"]["valid_till"]
            subscription_instance.renewal_due = data["subscription_data"]["renewal_due"]
            subscription_instance.save()

            subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

    @staticmethod
    def _generate_data_for_free_subscription(user_id: int, community_id: int, date_subscribed: int) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        date_subscribed = current_time if date_subscribed == 0 else date_subscribed

        data = {
            "subscription_data": {
                "user_id": user_id,
                "community_id": community_id,
                "plan_id": None,
                "date_subscribed": date_subscribed,
                "valid_till": lifetime_valid_till,
                "date_unsubscribed": None,
                "type": "free",
                "transaction": None
            }
        }

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], notify_period)

        data["subscription_history_data"] = {
            "start_date": date_subscribed,
            "end_date": data["subscription_data"]["valid_till"],
            "description": 'free subscription',
            "transaction": None,
            "type": "free",
            "user_id": user_id,
            "community_id": community_id
        }

        return data

    @staticmethod
    def _generate_free_subscription(user_id: int, community_id: int):

        subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

        if subscription_instance is None:
            data = SubscriptionImpl._generate_data_for_free_subscription(user_id, community_id, 0)

            subscription_instance = Subscription.create_instance(data['subscription_data'])
            subscription_history_instance = SubscriptionHistory.create_instance(
                data['subscription_history_data'])

            if not subscription_instance:
                return {'error_message': 'error creating subscription'}

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        else:
            data = SubscriptionImpl._generate_data_for_free_subscription(user_id,
                                                                         community_id,
                                                                         subscription_instance.date_subscribed)

            subscription_instance.plan_id = data['subscription_data']['plan_id']
            subscription_instance.date_subscribed = data['subscription_data']['date_subscribed']
            subscription_instance.valid_till = data['subscription_data']['valid_till']
            subscription_instance.type = data['subscription_data']['type']
            subscription_instance.renewal_due = data['subscription_data']['renewal_due']
            subscription_instance.transaction = data['subscription_data']['transaction']
            subscription_instance.save()

            subscription_history_instance = SubscriptionHistory.create_instance(
                data['subscription_history_data'])

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

    @staticmethod
    def _get_member_state(community_id: int, member_id: int) -> dict:

        if not community_id or not member_id:
            return {'error_message': 'send community_id and user_id'}

        url = member_state_api
        query_params = {
            'community_id': community_id,
            'member_id': member_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        data = {'is_owner': response['member']['is_owner']}

        return data

    @staticmethod
    def _verify_aj(community_id: int, user_id: int, aj: int):

        if not community_id or not user_id or not aj:
            return {'error_message': 'insufficient values sent'}

        url = community_questions_api
        query_params = {
            'community_id': community_id,
            'aj': aj
        }
        headers = {
            'x-member-id': '{}'.format(user_id)
        }

        response = ApiUtilities.generate_get_request(url=url, headers=headers, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        return {'aj_expired': response['aj_expired']}

    def create_subscription(self, subscription_body: dict, user_id: str) -> dict:

        user_id = NumberUtilities.get_integer_from_string(user_id)

        if 'payment_id' in subscription_body:

            transaction_validation = self._check_if_transaction_is_used(subscription_body['payment_id'])

            if 'error_message' in transaction_validation:
                return {'error_message': transaction_validation['error_message']}

            if 'abort_execution' in transaction_validation:
                return {'abort_execution': transaction_validation['abort_execution']}

            transaction_instance = transaction_validation['transaction']

            generate_subscription = self._generate_subscription_against_transaction(transaction_instance, user_id)

            if 'error_message' in generate_subscription:
                return {'error_message': generate_subscription['error_message']}

        elif 'community_id' in subscription_body and 'type' in subscription_body:

            community_id = NumberUtilities.get_integer_from_string(subscription_body['community_id'])

            member_state = self._get_member_state(community_id, user_id)
            is_owner = member_state['is_owner']

            if is_owner:

                generate_free_subscription = self._generate_free_subscription(user_id, community_id)

                if 'error_message' in generate_free_subscription:
                    return {'error_message': generate_free_subscription['error_message']}

                return {'success': True}

            if 'aj' in subscription_body:

                aj = NumberUtilities.get_integer_from_string(subscription_body['aj'])

                verify_aj = self._verify_aj(community_id, user_id, aj)

                if 'error_message' in verify_aj:
                    return {'error_message': verify_aj['error_message']}

                aj_expired = verify_aj['aj_expired']

                if aj_expired:
                    return {'error_message': 'Link expired'}

                generate_free_subscription = self._generate_free_subscription(user_id, community_id)

                if 'error_message' in generate_free_subscription:
                    return {'error_message': generate_free_subscription['error_message']}

                return {'success': True}

    def start_subscription(self, request_body: dict) -> dict:

        user_id = NumberUtilities.get_integer_from_string(request_body['user_id'])
        community_id = NumberUtilities.get_integer_from_string(request_body['community_id'])

        subscription_instance = Subscription.get_subscription_or_None(user_id=user_id, community_id=community_id)

        if subscription_instance is None:
            return {'error_message': 'no subscription exists for provided user_id and community_id'}

        if subscription_instance.created_at == subscription_instance.updated_at:
            current_time = TimeUtilities.current_time_in_milliseconds()

            difference = current_time - subscription_instance.date_subscribed

            subscription_instance.date_subscribed = current_time
            subscription_instance.valid_till = TimeUtilities.add_milliseconds_in_epoch_time(current_time, difference)
            subscription_instance.save()

            return {'success': True}

        return {'error_message': 'something went wrong'}

    @staticmethod
    def _fetch_subscriptions(user_id: int, community_id: int):
        if community_id is not None:
            return Subscription.objects.filter(user_id=user_id, community_id=community_id).order_by('created_at')
        return Subscription.objects.filter(user_id=user_id).order_by('created_at')

    @staticmethod
    def _serialize_subscriptions(subscriptions):
        return SubscriptionSerializer(subscriptions)

    def fetch_subscription(self, user_id: str, community_id: str) -> object:

        user_id = NumberUtilities.get_integer_from_string(user_id)
        community_id = NumberUtilities.get_integer_from_string(community_id) if community_id else None

        subscriptions = self._fetch_subscriptions(user_id, community_id)

        if len(subscriptions) == 0:
            return {'error_message': 'no subscriptions exist with provided user_id'}

        return self._serialize_subscriptions(subscriptions)

    @staticmethod
    def _fetch_subscription_history(user_id: int, community_id: int):
        return SubscriptionHistory.objects.filter(user_id=user_id, community_id=community_id).order_by('created_at')

    @staticmethod
    def _serialize_subscription_history(subscription_history):
        return SubscriptionHistorySerializer(subscription_history)

    def fetch_subscription_history(self, user_id: str, community_id: str) -> object:

        user_id = NumberUtilities.get_integer_from_string(user_id)
        community_id = NumberUtilities.get_integer_from_string(community_id)

        subscription_history = self._fetch_subscription_history(user_id, community_id)

        if len(subscription_history) == 0:
            return {'error_message': 'no subscription history exist with provided user_id and community_id'}

        return self._serialize_subscription_history(subscription_history)

    def fetch_community_meta(self, payment_id: str) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=payment_id)

        if transaction_instance is None:
            return {'error_message': 'Incorrect payment ID'}

        if transaction_instance.user_id is not None:
            return {'error_message': 'Payment ID already used'}

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'cannot retrieve community_id'}

        return {'community_id': plan_instance.community_id}
