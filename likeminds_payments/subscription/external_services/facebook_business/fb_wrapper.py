import time

from facebook_business.adobjects.serverside.action_source import ActionSource
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.api import FacebookAdsApi

from ..facebook_business.fb_manager import FbManager
from django.conf import settings


class FbWrapper(FbManager):

    __instance_created__ = False

    def __init__(self) -> None:

        FacebookAdsApi.init(access_token=settings.FB_ACCESS_TOKEN)

        FbWrapper.__instance_created__ = True

    @staticmethod
    def create_user(client_ip_address: str, client_user_agent: str, emails: list = None, phones: list = None,
                    fbc: str = None, fbp: str = None):
        user_data = UserData(
            emails=emails if emails is not None else [],
            phones=phones if phones is not None else [],
            client_ip_address=client_ip_address,
            client_user_agent=client_user_agent,
            fbc=fbc if fbc is not None else '',
            fbp=fbp if fbp is not None else '',
        )

        return user_data

    @staticmethod
    def create_event(event_name: str, action_source: str, user_data: UserData, event_source_url: str = None):

        action_source_value = ActionSource.OTHER

        if action_source in ActionSource.__members__:
            action_source_value = ActionSource[action_source]

        event = Event(
            event_name=event_name,
            event_time=int(time.time()),
            user_data=user_data,
            event_source_url=event_source_url if event_source_url is not None else '',
            action_source=action_source_value
        )

        return event

    @staticmethod
    def send_event(events: list):

        if not FbWrapper.__instance_created__:
            FbWrapper()

        event_request = EventRequest(
            events=events,
            pixel_id=settings.FB_PIXEL_ID,
            test_event_code="TEST88709" if settings.IS_BETA else None
        )

        event_request.execute()
