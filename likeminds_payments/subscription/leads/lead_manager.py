import abc


class LeadManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'send_facebook_event') and callable(subclass.send_facebook_event)) or
                NotImplemented)

    @abc.abstractmethod
    def send_facebook_event(self, client_ip_address: str, client_user_agent: str, event_name: str,
                            action_source: str, emails: list, phones: list, fbc: str, fbp: str,
                            event_source_url: str) -> dict:
        """
        sends facebook event for a conversion
        """
        raise NotImplementedError
