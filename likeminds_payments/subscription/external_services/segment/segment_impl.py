from .segment_manager import SegmentManager
from ..logging.logging_wrapper import LoggingWrapper
from django.conf import settings

import analytics

error_logger = LoggingWrapper.get_instance()
info_logger = LoggingWrapper.get_instance()


class SegmentImpl(SegmentManager):

    @staticmethod
    def track_event(user_id, event_name, event_data) -> None:
        analytics.write_key = settings.SEGMENT_KEY

        try:
            analytics.track(user_id, event_name, event_data)

        except Exception as e:
            error_logger.error(e)
