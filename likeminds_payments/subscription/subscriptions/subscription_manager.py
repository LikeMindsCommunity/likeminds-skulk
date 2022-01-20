import abc


class SubscriptionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_subscription') and callable(subclass.create_subscription)) and
                (hasattr(subclass, 'start_subscription') and callable(subclass.start_subscription)) and
                (hasattr(subclass, 'fetch_subscription') and callable(subclass.fetch_subscription)) and
                (hasattr(subclass, 'fetch_community_meta') and callable(subclass.fetch_community_meta)) and
                (hasattr(subclass, 'convert_to_paid') and callable(subclass.convert_to_paid)) and
                (hasattr(subclass, 'external_migration') and callable(subclass.external_migration)) and
                (hasattr(subclass, 'external_renew_migrate') and callable(subclass.external_renew_migrate)) and
                (hasattr(subclass, 'payment_page_add_cash') and callable(subclass.payment_page_add_cash)) and
                (hasattr(subclass, 'members_report') and callable(subclass.members_report)) and
                (hasattr(subclass, 'fetch_community_renewals') and callable(subclass.fetch_community_renewals)) and
                (hasattr(subclass, 'fetch_subscription_meta') and callable(subclass.fetch_subscription_meta)) or
                NotImplemented)

    @abc.abstractmethod
    def create_subscription(self) -> dict:
        """
        create subscription_files from the payment
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start_subscription(self) -> dict:
        """
        start subscription_files of a specific user for given community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_subscription(self) -> dict:
        """
        fetch all the subscriptions of a user
        (a single subscription_files, if community_id is provided)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_community_meta(self) -> dict:
        """
        get community meta details for given payment_id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def convert_to_paid(self) -> dict:
        """
        convert free internal communities to paid
        """
        raise NotImplementedError

    @abc.abstractmethod
    def external_migration(self, request_body: dict) -> dict:
        """
        migrate external communities
        """
        raise NotImplementedError

    @abc.abstractmethod
    def external_renew_migrate(self, request_body: dict) -> dict:
        """
        migrate renew cash payments
        """
        raise NotImplementedError

    @abc.abstractmethod
    def payment_page_add_cash(self, request_body: dict) -> dict:
        """
        add cash from payment pages
        """
        raise NotImplementedError

    @abc.abstractmethod
    def members_report(self) -> dict:
        """
        sends member details of a community to the cm
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_community_renewals(self) -> dict:
        """
        sends upcoming renewals in a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_subscription_meta(self) -> dict:
        """
        fetch subscription meta for a community
        """
        raise NotImplementedError
