import abc


class SubscriptionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'fetch_subscription_history') and callable(subclass.fetch_subscription_history)) and
                (hasattr(subclass, 'fetch_community_meta') and callable(subclass.fetch_community_meta)) or
                NotImplemented)

    @abc.abstractmethod
    def fetch_subscription_history(self, user_id: str, community_id: str) -> object:
        """
        fetch all the subscriptions history for a user for a given community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_community_meta(self, payment_id: str) -> dict:
        """
        get community meta details for given payment_id
        """
        raise NotImplementedError
