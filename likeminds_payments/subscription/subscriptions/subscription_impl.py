from .subscription_manager import SubscriptionManager
from ..transactions.models import Transaction
from .models import Subscription
from ..subscription_histories.models import SubscriptionHistory
from ..plans.models import SubscriptionPlan
from .constants import *
from .serializers import SubscriptionSerializer

from ..utility.time_utilities import TimeUtilities
from ..utility.api_utilities import ApiUtilities
from ..utility.number_utilities import NumberUtilities
from ..plans.constants import *
from ..transactions.constants import *
from ..orders.constants import *


class SubscriptionImpl(SubscriptionManager):

    payment_id = None
    user_id = None
    community_id = None
    subscription_type = None
    aj = None
    free_user_id = None

    def __init__(self, payment_id: str = None, user_id: str = None, community_id: str = None,
                 subscription_type: str = None, aj: str = None, free_user_id: str = None):
        self.payment_id = payment_id
        self.user_id = user_id
        self.community_id = community_id
        self.subscription_type = subscription_type
        self.aj = aj
        self.free_user_id = free_user_id

    def get_payment_id(self) -> str:
        return self.payment_id

    def get_user_id(self) -> str:
        return self.user_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_subscription_type(self) -> str:
        return self.subscription_type

    def get_aj(self) -> str:
        return self.aj

    def get_free_user_id(self) -> str:
        return self.free_user_id

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
                "valid_till": TimeUtilities.subtract_days_in_epoch_time(TimeUtilities.add_days_in_epoch_time(
                    existing_valid_till, subscription_plan_instance.referral_free_days), 1)
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
        subscription_instance.save()

        subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

        if not subscription_history_instance:
            return {'error_message': 'error creating subscription history'}

        return {'success': True}

    @staticmethod
    def _generate_subscription_against_transaction(transaction_instance: dict, user_id: int) -> dict:

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

        url = MEMBER_STATE_API
        query_params = {
            'community_id': community_id,
            'member_id': member_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        data = {'is_owner': False}

        if response['state'] == 1:
            data = {'is_owner': True}

        return data

    @staticmethod
    def _verify_aj(community_id: int, user_id: int, aj: int):

        if not community_id or not user_id or not aj:
            return {'error_message': 'insufficient values sent'}

        url = COMMUNITY_QUESTIONS_API
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

    def create_subscription(self) -> dict:

        user_id = NumberUtilities.get_integer_from_string(self.get_user_id())

        if self.get_payment_id() is not None:

            transaction_validation = self._check_if_transaction_is_used(self.get_payment_id())

            if 'error_message' in transaction_validation:
                return {'error_message': transaction_validation['error_message']}

            if 'abort_execution' in transaction_validation:
                return {'abort_execution': transaction_validation['abort_execution']}

            transaction_instance = transaction_validation['transaction']

            generate_subscription = self._generate_subscription_against_transaction(transaction_instance, user_id)

            if 'error_message' in generate_subscription:
                return {'error_message': generate_subscription['error_message']}

            return {'success': True}

        elif self.get_community_id() is not None and self.get_subscription_type() is not None:

            community_id = NumberUtilities.get_integer_from_string(self.get_community_id())
            free_user_id = NumberUtilities.get_integer_from_string(self.get_free_user_id())

            member_state = self._get_member_state(community_id, user_id)

            if 'error_message' in member_state:
                return {'error_message': member_state['error_message']}

            is_owner = member_state['is_owner']

            if is_owner:

                free_member_state = self._get_member_state(community_id, free_user_id)

                if 'error_message' in free_member_state:
                    return {'error_message': free_member_state['error_message']}

                is_free_member_owner = free_member_state['is_owner']

                if is_free_member_owner:

                    generate_free_subscription = self._generate_free_subscription(free_user_id, community_id)

                    if 'error_message' in generate_free_subscription:
                        return {'error_message': generate_free_subscription['error_message']}

                    return {'success': True}

                if self.get_aj() is not None:

                    aj = NumberUtilities.get_integer_from_string(self.get_aj())

                    verify_aj = self._verify_aj(community_id, free_user_id, aj)

                    if 'error_message' in verify_aj:
                        return {'error_message': verify_aj['error_message']}

                    aj_expired = verify_aj['aj_expired']

                    if aj_expired:
                        return {'error_message': 'Link expired'}

                    generate_free_subscription = self._generate_free_subscription(free_user_id, community_id)

                    if 'error_message' in generate_free_subscription:
                        return {'error_message': generate_free_subscription['error_message']}

                    return {'success': True}

            return {'error_message': 'you are not allowed to give free subscriptions'}

    def start_subscription(self) -> dict:

        user_id = NumberUtilities.get_integer_from_string(self.get_user_id())
        community_id = NumberUtilities.get_integer_from_string(self.get_community_id())

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

    def fetch_subscription(self) -> dict:

        user_id = NumberUtilities.get_integer_from_string(self.get_user_id())
        community_id = NumberUtilities.get_integer_from_string(self.get_community_id())

        subscriptions = self._fetch_subscriptions(user_id, community_id)

        if len(subscriptions) == 0:
            return {'error_message': 'no subscriptions exist with provided user_id'}

        return {'subscriptions': self._serialize_subscriptions(subscriptions)}

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
