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
                (hasattr(subclass, 'update_transaction') and callable(subclass.update_transaction)) and
                (hasattr(subclass, 'create_subscription') and callable(subclass.create_subscription)) or
                NotImplemented)

    @abc.abstractmethod
    def create_plan(self, plan_body: dict) -> dict:
        """
        create a new plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_plan(self, community_id: str) -> dict:
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
    def create_transaction(self, transaction_body: dict) -> dict:
        """
        create a transaction from razorpay webhook
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_transaction(self, payment_id: str) -> dict:
        """
        update an existing transaction
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_subscription(self, payment_id: str) -> dict:
        """
        create subscription from the payment
        """
        raise NotImplementedError
