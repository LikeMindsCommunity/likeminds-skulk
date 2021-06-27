import abc


class SubscriptionHistoryManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'fetch_subscription_history') and callable(subclass.fetch_subscription_history)) or
                NotImplemented)

    @abc.abstractmethod
    def fetch_subscription_history(self) -> dict:
        """
        fetch all the subscriptions history for a user for a given community
        """
        raise NotImplementedError
