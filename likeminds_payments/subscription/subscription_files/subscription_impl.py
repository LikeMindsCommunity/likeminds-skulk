from ..subscription_files.subscription_manager import SubscriptionManager
from ..subscription_files.serializers import SubscriptionHistorySerializer
from ..utility.number_utilities import NumberUtilities

from ..models import Transaction, SubscriptionHistory
from ..plans.models import SubscriptionPlan


class SubscriptionImpl(SubscriptionManager):

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
