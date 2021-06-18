import abc


class SubscriptionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_subscription') and callable(subclass.create_subscription)) and
                (hasattr(subclass, 'start_subscription') and callable(subclass.start_subscription)) and
                (hasattr(subclass, 'fetch_subscription') and callable(subclass.fetch_subscription)) or
                NotImplemented)

    @abc.abstractmethod
    def create_subscription(self) -> dict:
        """
        create subscription_files from the payment
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start_subscription(self) -> dict:
        """
        start subscription_files of a specific user for given community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_subscription(self) -> dict:
        """
        fetch all the subscriptions of a user
        (a single subscription_files, if community_id is provided)
        """
        raise NotImplementedError
