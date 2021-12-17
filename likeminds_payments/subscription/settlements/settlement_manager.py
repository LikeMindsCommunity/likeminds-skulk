import abc


class SettlementManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'initiate_settlement') and callable(subclass.initiate_settlement)) and
                (hasattr(subclass, 'create_settlement') and callable(subclass.create_settlement)) and
                (hasattr(subclass, 'fetch_settlement') and callable(subclass.fetch_settlement))
                or
                NotImplemented)

    @abc.abstractmethod
    def initiate_settlement(self) -> dict:
        """
        initiate settlement for a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_settlement(self) -> dict:
        """
        create settlement for a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_settlement(self) -> dict:
        """
        Fetch settlement for a community
        """
        raise NotImplementedError
