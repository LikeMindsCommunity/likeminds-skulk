import abc


class RazorpayXManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_contact') and callable(subclass.create_contact)) and
                (hasattr(subclass, 'create_fund_account') and callable(subclass.create_fund_account))
                or NotImplemented)

    def create_contact(self, contact_info) -> dict:
        """
        creates a contact in razorpayX
        """
        raise NotImplementedError

    def create_fund_account(self, account_info) -> dict:
        """
        creates a fund account in razorpayX
        """
        raise NotImplementedError
