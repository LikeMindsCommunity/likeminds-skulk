import abc
from facebook_business.adobjects.serverside.user_data import UserData


class FbManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_user') and callable(subclass.create_user)) and
                (hasattr(subclass, 'create_event') and callable(subclass.create_event)) and
                (hasattr(subclass, 'send_event') and callable(subclass.send_event)) or
                NotImplemented)

    @staticmethod
    def create_user(client_ip_address: str, client_user_agent: str, emails: list = None, phones: list = None,
                    fbc: str = None, fbp: str = None):
        """
        creates a facebook user instance
        """
        raise NotImplementedError

    @staticmethod
    def create_event(event_name: str, action_source: str, user_data: UserData, event_source_url: str = None):
        """
        creates a facebook event
        """
        raise NotImplementedError

    @staticmethod
    def send_event(events: list) -> dict:
        """
        sends the facebook events
        """
        raise NotImplementedError
