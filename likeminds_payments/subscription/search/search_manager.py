import abc


class SearchManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'search_plan') and callable(subclass.search_plan)) and
                ((hasattr(subclass, 'search_history') and callable(subclass.search_history)) or
                 NotImplemented))

    @abc.abstractmethod
    def search_plan(self) -> dict:
        """
        Search subscription using plan_sub_title
        @return: dict
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search_history(self) -> dict:
        """
        Search subscription history using plan_sub_title
        @return: dict
        """
        raise NotImplementedError
