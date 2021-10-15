import abc


class TransactionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_transaction') and callable(subclass.create_transaction)) and
                (hasattr(subclass, 'fetch_transactions') and callable(subclass.fetch_transactions)) and
                (hasattr(subclass, 'refund_transaction') and callable(subclass.refund_transaction)) and
                (hasattr(subclass, 'valid_event_transaction') and callable(subclass.valid_event_transaction)) and
                (hasattr(subclass, 'valid_event_payment_id') and callable(subclass.valid_event_payment_id)) and
                (hasattr(subclass, 'update_payment_id') and callable(subclass.update_payment_id))
                or
                NotImplemented)

    @abc.abstractmethod
    def create_transaction(self) -> dict:
        """
        create a transaction from razorpay webhook
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_transactions(self, page, payment_page_id) -> dict:
        """
        Fetch transactions of a user in a community or all the unmapped transactions in a community
        """
        raise NotImplementedError

    @staticmethod
    def refund_transaction(self) -> dict:
        """
        Refunds a transaction
        """
        raise NotImplementedError

    @abc.abstractmethod
    def valid_event_transaction(self, chatroom_id, user_id) -> dict:
        """
        create a check if event transaction is valid or not
        """

        raise NotImplementedError

    @abc.abstractmethod
    def valid_event_payment_id(self, payment_id, user_id) -> dict:
        """
        create if the payment id is valid or not
        """

        raise NotImplementedError

    @abc.abstractmethod
    def update_payment_id(self, req_body, user_id) -> dict:
        """
        updates the payment id and user
        """

        raise NotImplementedError
