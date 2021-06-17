import abc


class PlanManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_plan') and callable(subclass.create_plan)) and
                (hasattr(subclass, 'fetch_plan') and callable(subclass.fetch_plan)) and
                (hasattr(subclass, 'delete_plan') and callable(subclass.delete_plan)) or
                NotImplemented)

    @abc.abstractmethod
    def create_plan(self) -> dict:
        """
        create a new plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_plan(self) -> dict:
        """
        fetch all the plans of a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_plan(self) -> dict:
        """
        delete an existing plan
        """
        raise NotImplementedError
