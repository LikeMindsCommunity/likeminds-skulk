from .subscription_manager import SubscriptionManager
from ..transactions.models import Transaction
from .models import Subscription
from ..subscription_histories.models import SubscriptionHistory
from ..plans.models import SubscriptionPlan
from ..member_notifications.models import MemberNotification
from .constants import *
from .serializers import SubscriptionSerializer, SubscriptionListSerializer

from ..utility.time_utilities import TimeUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper
from ..plans.constants import *
from ..transactions.constants import *

import razorpay


class SubscriptionImpl(SubscriptionManager):

    payment_id = None
    user_id = None
    community_id = None
    subscription_type = None
    member_id = None

    def __init__(self, payment_id: str = None, user_id: str = None, community_id: str = None,
                 subscription_type: str = None, member_id: str = None):
        self.payment_id = payment_id
        self.user_id = user_id
        self.community_id = community_id
        self.subscription_type = subscription_type
        self.member_id = member_id

    def get_payment_id(self) -> str:
        return self.payment_id

    def get_user_id(self) -> str:
        return self.user_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_subscription_type(self) -> str:
        return self.subscription_type

    def get_member_id(self) -> str:
        return self.member_id

    @staticmethod
    def _remove_member_notifications(user_id: str, community_id: str):

        MemberNotification.objects.filter(user_id=user_id, community_id=community_id).delete()

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

        if subscription_plan_instance.duration_in_months == SUBSCRIPTION_PLAN_CHOICES["lifetime"]:
            data["subscription_data"]["type"] = LIFETIME_PAYMENT
            data["subscription_data"]["valid_till"] = LIFETIME_VALID_TILL

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": ONETIME_DESCRIPTION,
            "transaction": transaction_instance,
            "type": "paid",
            "user_id": user_id,
            "community_id": subscription_plan_instance.community_id
        }

        if subscription_plan_instance.duration_in_months == SUBSCRIPTION_PLAN_CHOICES["lifetime"]:
            data["subscription_history_data"]["description"] = LIFETIME_DESCRIPTION

        return data

    @staticmethod
    def _generate_data_for_existing_subscription_against_transaction(subscription_instance: dict,
                                                                     subscription_plan_instance: dict,
                                                                     transaction_instance: dict) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        data = {
            "subscription_data": {
                "type": "onetime",
                "valid_till": 0,
                "transaction": transaction_instance
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
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": RENEWAL_DESCRIPTION,
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
                "valid_till": TimeUtilities.add_days_in_epoch_time(
                    existing_valid_till, subscription_plan_instance.referral_free_days)
            }
        }

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

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
    def _generate_first_transaction(transaction_instance: dict, plan_instance: dict, user_id: int):

        if transaction_instance.user_id is None:
            transaction_instance.user_id = user_id
            transaction_instance.save()

            subscription_instance = Subscription.get_subscription_or_None(user_id, plan_instance.community_id)

            if subscription_instance is not None:
                renewal = SubscriptionImpl._generate_renewal_transaction(transaction_instance, plan_instance, user_id)
                return renewal

            data = SubscriptionImpl._generate_data_for_new_subscription_against_transaction(
                transaction_instance, plan_instance, user_id)

            subscription_instance = Subscription.create_instance(data['subscription_data'])
            subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

            if transaction_instance.shared_by is not None:
                referrer_subscription_instance = Subscription.get_subscription_or_None(
                    transaction_instance.shared_by, plan_instance.community_id
                )

                if referrer_subscription_instance.type != ONETIME_PAYMENT:
                    return {'error_message': 'referrer user is not having onetime subscription'}

                referrer_data = SubscriptionImpl._generate_data_for_existing_subscription_against_referral(
                    referrer_subscription_instance, plan_instance, transaction_instance)

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

    @staticmethod
    def _generate_renewal_transaction(transaction_instance: dict, plan_instance: dict, user_id):

        if transaction_instance.user_id is None:
            return {'error_message': "user ID doesn't exist for renewal transaction"}

        if transaction_instance.user_id != user_id:
            return {'error_message': 'Invalid user ID'}

        subscription_instance = Subscription.get_subscription_or_None(
            transaction_instance.user_id, plan_instance.community_id
        )

        if not subscription_instance:
            return {'error_message': 'no subscription exists for given user in given community'}

        if subscription_instance.type == LIFETIME_PAYMENT:
            return {'error_message': 'cannot renew a lifetime subscription'}

        data = SubscriptionImpl._generate_data_for_existing_subscription_against_transaction(
            subscription_instance, plan_instance, transaction_instance)

        subscription_instance.type = data["subscription_data"]["type"]
        subscription_instance.valid_till = data["subscription_data"]["valid_till"]
        subscription_instance.renewal_due = data["subscription_data"]["renewal_due"]
        subscription_instance.transaction = data["subscription_data"]["transaction"]
        subscription_instance.is_removed = False
        subscription_instance.save()

        SubscriptionImpl._remove_member_notifications(subscription_instance.user_id, subscription_instance.community_id)

        subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

        if not subscription_history_instance:
            return {'error_message': 'error creating subscription history'}

        return {'success': True}

    @staticmethod
    def _generate_subscription_against_transaction(transaction_instance: dict, user_id: str) -> dict:

        user_id = NumberUtilities.get_integer_from_string(user_id)
        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'no plan exist for this transaction, contact your cm.'}

        if not transaction_instance.renew:

            transaction = SubscriptionImpl._generate_first_transaction(transaction_instance, plan_instance, user_id)
            return transaction

        if transaction_instance.renew:

            transaction = SubscriptionImpl._generate_renewal_transaction(transaction_instance, plan_instance, user_id)
            return transaction

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
                "valid_till": LIFETIME_VALID_TILL,
                "date_unsubscribed": None,
                "type": "free",
                "transaction": None
            }
        }

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": date_subscribed,
            "end_date": data["subscription_data"]["valid_till"],
            "description": FREE_DESCRIPTION,
            "transaction": None,
            "type": "free",
            "user_id": user_id,
            "community_id": community_id
        }

        return data

    @staticmethod
    def _generate_free_subscription(user_id: str, community_id: str):

        user_id = NumberUtilities.get_integer_from_string(user_id)
        community_id = NumberUtilities.get_integer_from_string(community_id)

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
            subscription_instance.is_removed = False
            subscription_instance.save()

            SubscriptionImpl._remove_member_notifications(subscription_instance.user_id,
                                                          subscription_instance.community_id)

            subscription_history_instance = SubscriptionHistory.create_instance(
                data['subscription_history_data'])

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

    @staticmethod
    def _add_free_days_to_subscription(user_id: str, community_id: str, valid_till: str, n_days: str):

        user_id = NumberUtilities.get_integer_from_string(user_id)
        community_id = NumberUtilities.get_integer_from_string(community_id)
        valid_till = NumberUtilities.get_integer_from_string(valid_till)
        n_days = NumberUtilities.get_integer_from_string(n_days)
        subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

        if subscription_instance is not None:

            if valid_till is not None and valid_till > subscription_instance.valid_till and n_days is None:
                subscription_instance.valid_till = valid_till

            if valid_till is None and n_days is not None:
                subscription_instance.valid_till = TimeUtilities.add_days_in_epoch_time(
                    subscription_instance.valid_till, n_days)

            subscription_instance.save()

            subscription_history_data = {
                "start_date": subscription_instance.date_subscribed,
                "end_date": subscription_instance.valid_till,
                "description": 'free limited subscription',
                "transaction": None,
                "type": "free",
                "user_id": user_id,
                "community_id": community_id
            }

            subscription_history_instance = SubscriptionHistory.create_instance(subscription_history_data)

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        return {'error_message': 'invalid user_id and community_id pair'}

    def create_subscription(self, n_days: str = None, valid_till: str = None, shared_by: str = None) -> dict:

        if self.get_payment_id() is not None:

            transaction_validation = self._check_if_transaction_is_used(self.get_payment_id())

            if 'error_message' in transaction_validation:
                return {'error_message': transaction_validation['error_message']}

            if 'abort_execution' in transaction_validation:
                return {'abort_execution': transaction_validation['abort_execution']}

            transaction_instance = transaction_validation['transaction']

            generate_subscription = self._generate_subscription_against_transaction(transaction_instance,
                                                                                    self.get_member_id())

            if 'error_message' in generate_subscription:
                return {'error_message': generate_subscription['error_message']}

            return {'success': True}

        elif self.get_community_id() is not None and self.get_subscription_type() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check:
                if has_permission_check['has_permission'] is False and shared_by is None:
                    return {'error_message': 'You are not the Owner/CM of the community'}

                if self.get_subscription_type() == DASHBOARD:

                    add_free_days = self._add_free_days_to_subscription(self.get_user_id(),
                                                                        self.get_community_id(),
                                                                        valid_till, n_days)

                    if 'error_message' in add_free_days:
                        return {'error_message': add_free_days['error_message']}

                    return {'success': True}

                if self.get_subscription_type() == FREE_SUBSCRIPTION:

                    if shared_by is None:

                        generate_free_subscription = self._generate_free_subscription(self.get_user_id(),
                                                                                      self.get_community_id())

                        if 'error_message' in generate_free_subscription:
                            return {'error_message': generate_free_subscription['error_message']}

                        return {'success': True}

                    has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), shared_by)

                    if 'error_message' in has_permission_check:
                        return {'error_message': has_permission_check['error_message']}

                    if 'has_permission' in has_permission_check:
                        if has_permission_check['has_permission'] is False:
                            return {'error_message': 'shared_by user is not the Owner/CM of the community'}

                        generate_free_subscription = self._generate_free_subscription(self.get_user_id(),
                                                                                      self.get_community_id())

                        if 'error_message' in generate_free_subscription:
                            return {'error_message': generate_free_subscription['error_message']}

                        return {'success': True}

            return {'error_message': 'You are not Owner/CM of this community'}

    def start_subscription(self) -> dict:

        subscription_instance = Subscription.get_subscription_or_None(user_id=self.get_member_id(),
                                                                      community_id=self.get_community_id())

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
    def _fetch_subscriptions(user_id: str, community_id: str):
        if community_id is not None:
            return Subscription.objects.filter(user_id=user_id, community_id=community_id).order_by('created_at')
        return Subscription.objects.filter(user_id=user_id).order_by('created_at')

    @staticmethod
    def _serialize_subscriptions(subscriptions):
        return SubscriptionSerializer(subscriptions)

    @staticmethod
    def _serialize_subscriptions_list(subscriptions):
        return SubscriptionListSerializer(subscriptions)

    def fetch_subscription(self, member_ids: list = None) -> dict:

        if member_ids is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            member_subscriptions = {}

            for member_id in member_ids:
                member_subscriptions[member_id] = self._fetch_subscriptions(member_id, self.get_community_id())

            return {'subscriptions': self._serialize_subscriptions_list(member_subscriptions)}

        subscriptions = self._fetch_subscriptions(self.get_member_id(), self.get_community_id())

        if len(subscriptions) == 0:
            return {'error_message': 'no subscriptions exist with provided user_id'}

        return {'subscriptions': self._serialize_subscriptions(subscriptions)}

    def cancel_subscription(self) -> dict:

        if self.get_user_id() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            subscription_instance = Subscription.get_subscription_or_None(user_id=self.get_user_id(),
                                                                          community_id=self.get_community_id())

        else:

            is_pending_member = CoreServiceUtilities.is_pending_member(self.get_community_id(), self.get_member_id())

            if 'error_message' in is_pending_member:
                return {'error_message': is_pending_member['error_message']}

            if is_pending_member['is_pending_member'] is False:
                return {'error_message': 'Your are not a pending member'}

            subscription_instance = Subscription.get_subscription_or_None(self.get_member_id(), self.get_community_id())

        if subscription_instance is None:
            return {'error_message': 'no subscription exists for this user_id and community_id'}

        if subscription_instance.transaction is None:
            return {'error_message': 'no active payment associated with this user subscription to be refunded'}

        razorpay_client = RazorpayWrapper.get_instance()

        try:
            response = razorpay_client.payment.refund(subscription_instance.transaction.payment_id,
                                                      subscription_instance.transaction.amount)
        except razorpay.errors.BadRequestError as e:
            return {'error_message': e.__str__()}

        try:
            subscription_instance.delete()
        except:
            return {'error_message': 'something went wrong'}

        return response

    def fetch_community_meta(self) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=self.get_payment_id())

        if transaction_instance is None:
            return {'error_message': 'Incorrect payment ID'}

        if transaction_instance.user_id is not None:
            return {'error_message': 'Payment ID already used'}

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'cannot retrieve community_id'}

        return {'community_id': plan_instance.community_id}
