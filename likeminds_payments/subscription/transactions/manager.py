import abc


class TransactionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_transaction') and callable(subclass.create_transaction)) or
                NotImplemented)

    @abc.abstractmethod
    def create_transaction(self) -> dict:
        """
        create a transaction from razorpay webhook
        """
        raise NotImplementedError
