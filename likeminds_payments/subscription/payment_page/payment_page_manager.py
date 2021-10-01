import abc


class PaymentPageManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'fetch_all_payment_page') and callable(subclass.fetch_all_payment_page)) and
                (hasattr(subclass, 'fetch_payment_page') and callable(subclass.fetch_payment_page)) and
                (hasattr(subclass, 'fetch_contact_us') and callable(subclass.fetch_contact_us)) or
                NotImplemented)

    @abc.abstractmethod
    def fetch_all_payment_page(self, req_body) -> dict:
        """
        This fetches all the payment page corresponding to a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_payment_page(self, payment_page_id) -> dict:
        """
        This fetches the payment page corresponding to a payment_page_id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_contact_us(self) -> dict:
        """
        This fetches contact details of the member
        """
        raise NotImplementedError
