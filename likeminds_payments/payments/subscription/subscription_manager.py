import abc


class SubscriptionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_plan') and callable(subclass.create_plan)) and
                (hasattr(subclass, 'fetch_plan') and callable(subclass.fetch_plan)) and
                (hasattr(subclass, 'delete_plan') and callable(subclass.delete_plan)) and
                (hasattr(subclass, 'create_order') and callable(subclass.create_order)) and
                (hasattr(subclass, 'verify_order') and callable(subclass.verify_order)) and
                (hasattr(subclass, 'create_transaction') and callable(subclass.create_transaction)) and
                (hasattr(subclass, 'create_subscription') and callable(subclass.create_subscription)) and
                (hasattr(subclass, 'start_subscription') and callable(subclass.start_subscription)) and
                (hasattr(subclass, 'fetch_subscription') and callable(subclass.fetch_subscription)) and
                (hasattr(subclass, 'fetch_subscription_history') and callable(subclass.fetch_subscription_history)) and
                (hasattr(subclass, 'fetch_community_meta') and callable(subclass.fetch_community_meta)) or
                NotImplemented)

    @abc.abstractmethod
    def create_plan(self, plan_body: dict) -> dict:
        """
        create a new plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_plan(self, community_id: str) -> object:
        """
        fetch all the plans of a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_plan(self, plan_id: str) -> dict:
        """
        delete an existing plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_order(self, order_body: dict) -> dict:
        """
        create an order for an existing plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify_order(self, payment_body: dict) -> dict:
        """
        verify the payment for an order
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_transaction(self, transaction_body: dict, transaction_raw_body, transaction_signature: str) -> dict:
        """
        create a transaction from razorpay webhook
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_subscription(self, subscription_body: dict, user_id: str) -> dict:
        """
        create subscription from the payment
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start_subscription(self, request_body: dict) -> dict:
        """
        start subscription of a specific user for given community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_subscription(self, user_id: str, community_id: str) -> object:
        """
        fetch all the subscriptions of a user
        (a single subscription, if community_id is provided)
        """
        raise NotImplementedError

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
