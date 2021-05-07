import abc

class PlansManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_plan') and callable(subclass.create_plan)) or
        NotImplemented)

    @abc.abstractmethod
    def create_plan(self, req_body:dict) -> dict:
        """
        create a new plan
        """
        raise NotImplementedError
