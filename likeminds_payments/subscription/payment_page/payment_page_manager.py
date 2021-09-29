import abc


class PaymentPageManeger(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_payment_page') and callable(subclass.create_plan)) or
                NotImplemented)

    @abc.abstractmethod
    def create_payment_page(self) -> dict:
        """
        create a new payment page meta
        """
        raise NotImplementedError
