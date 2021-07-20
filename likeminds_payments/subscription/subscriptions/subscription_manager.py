import abc


class SubscriptionManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_subscription') and callable(subclass.create_subscription)) and
                (hasattr(subclass, 'start_subscription') and callable(subclass.start_subscription)) and
                (hasattr(subclass, 'fetch_subscription') and callable(subclass.fetch_subscription)) and
                (hasattr(subclass, 'fetch_community_meta') and callable(subclass.fetch_community_meta)) and
                (hasattr(subclass, 'convert_to_paid') and callable(subclass.convert_to_paid)) and
                (hasattr(subclass, 'create_event_plan') and callable(subclass.create_event_plan)) and
                (hasattr(subclass, 'fetch_event_plan') and callable(subclass.fetch_event_plan)) or
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
    def create_event_plan(self, req_body) -> dict:
        """
        create a plan for event
        """

        raise NotImplementedError

    @abc.abstractmethod
    def fetch_event_plan(self, chatroom_ids) -> dict:
        """
        return events of chatroom ids
        """

        raise NotImplementedError

