import abc

class OrdersManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_order') and callable(subclass.create_order)) and
        (hasattr(subclass, 'verify_order') and callable(subclass.verify_order)) or
        NotImplemented)

    @abc.abstractmethod
    def create_order(self, plan_id:str) -> dict:
        """
        generate a new order
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify_order(self, req_body:dict) -> dict:
        """
        verify a specific payment
        """
        raise NotImplementedError