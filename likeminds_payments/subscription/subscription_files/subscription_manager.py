import abc


class SubscriptionManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def fetch_community_meta(self, payment_id: str) -> dict:
        """
        get community meta details for given payment_id
        """
        raise NotImplementedError
