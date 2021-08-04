import abc


class OrderManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_order') and callable(subclass.create_order)) and
                (hasattr(subclass, 'verify_order') and callable(subclass.verify_order)) or
                NotImplemented)

    @abc.abstractmethod
    def create_order(self) -> dict:
        """
        create an order for an existing plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify_order(self) -> dict:
        """
        verify the payment for an order
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_event_order(self) -> dict:
        """
        create an order for an event
        """
        raise NotImplementedError

