import abc


class TransactionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_transaction') and callable(subclass.create_transaction)) and
                (hasattr(subclass, 'valid_event_transaction') and callable(subclass.valid_event_transaction))
                or
                NotImplemented)

    @abc.abstractmethod
    def create_transaction(self) -> dict:
        """
        create a transaction from razorpay webhook
        """
        raise NotImplementedError

    @abc.abstractmethod
    def valid_event_transaction(self, chatroom_id, user_id) -> dict:
        """
        create a check if event transaction is valid or not
        """
        raise NotImplementedError
