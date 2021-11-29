import abc


class SearchManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'search_plan') and callable(subclass.search_plan)) or
                NotImplemented)

    @abc.abstractmethod
    def search_plan(self):
        """
        Search subscription using plan_sub_title
        """
        raise NotImplementedError
