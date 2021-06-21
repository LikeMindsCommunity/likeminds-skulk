from .subscription_history_manager import SubscriptionHistoryManager
from .serializers import SubscriptionHistorySerializer

from .models import SubscriptionHistory


class SubscriptionHistoryImpl(SubscriptionHistoryManager):

    user_id = None
    community_id = None

    def __init__(self, user_id: str = None, community_id: str = None):
        self.user_id = user_id
        self.community_id = community_id

    def get_user_id(self) -> str:
        return self.user_id

    def get_community_id(self) -> str:
        return self.community_id

    @staticmethod
    def _fetch_subscription_history(user_id: str, community_id: str):
        return SubscriptionHistory.objects.filter(user_id=user_id, community_id=community_id).order_by('created_at')

    @staticmethod
    def _serialize_subscription_history(subscription_history):
        return SubscriptionHistorySerializer(subscription_history)

    def fetch_subscription_history(self) -> dict:

        subscription_history = self._fetch_subscription_history(self.get_user_id(), self.get_community_id())

        if len(subscription_history) == 0:
            return {'error_message': 'no subscription history exist with provided user_id and community_id'}

        return {'histories': self._serialize_subscription_history(subscription_history)}
