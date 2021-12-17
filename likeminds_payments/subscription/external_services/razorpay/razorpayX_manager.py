import abc


class RazorpayXManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_contact') and callable(subclass.create_contact)) and
                (hasattr(subclass, 'create_fund_account') and callable(subclass.create_fund_account)) and
                (hasattr(subclass, 'create_payout') and callable(subclass.create_payout))
                or NotImplemented)

    @abc.abstractmethod
    def create_contact(self, contact_info) -> dict:
        """
        creates a contact in razorpayX
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_fund_account(self, account_info) -> dict:
        """
        creates a fund account in razorpayX
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_payout(self, payout_info) -> dict:
        """
        creates a payout in razorpayX
        """
        raise NotImplementedError
