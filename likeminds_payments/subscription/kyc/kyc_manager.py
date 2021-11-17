import abc


class KYCManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'add_kyc') and callable(subclass.add_kyc)) and
                (hasattr(subclass, 'upload_kyc') and callable(subclass.upload_kyc)) and
                (hasattr(subclass, 'fetch_kyc') and callable(subclass.fetch_kyc)) and
                (hasattr(subclass, 'fetch_all_kyc') and callable(subclass.fetch_all_kyc)) and
                (hasattr(subclass, 'edit_kyc') and callable(subclass.edit_kyc))
                or
                NotImplemented)

    @abc.abstractmethod
    def add_kyc(self, request_body) -> dict:
        """
        create a kyc instance for a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def upload_kyc(self, request_body) -> dict:
        """
        upload kyc doc in a specific kyc instance
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_kyc(self) -> dict:
        """
        fetch kyc for a specific community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all_kyc(self) -> dict:
        """
        fetch all the kyc records
        """
        raise NotImplementedError

    @abc.abstractmethod
    def edit_kyc(self, request_body) -> dict:
        """
        edit kyc of a specific community
        """
        raise NotImplementedError
