from .lead_manager import LeadManager
from ..external_services.facebook_business.fb_wrapper import FbWrapper


class LeadImpl(LeadManager):

    def send_facebook_event(self, client_ip_address: str, client_user_agent: str, event_name: str,
                            action_source: str, emails: list = None, phones: list = None, fbc: str = None,
                            fbp: str = None, event_source_url: str = None) -> dict:

        user_instance = FbWrapper.create_user(client_ip_address, client_user_agent, emails, phones, fbc, fbp)
        event_instance = FbWrapper.create_event(event_name, action_source, user_instance, event_source_url)

        events = [event_instance]

        FbWrapper.send_event(events)

        return {'success': True}
