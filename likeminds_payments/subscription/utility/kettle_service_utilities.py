
from .constants import *
from ..utility.api_utilities import ApiUtilities
from ..external_services.logging.logging_wrapper import LoggingWrapper

error_logger = LoggingWrapper.get_instance()


class KettleServiceUtilities:

    @staticmethod
    def delete_cache(key_patterns: str) -> dict:

        headers = {
            'x-platform-type': SKULK_SERVICE_PLATFORM_TYPE
        }

        payload = {
            'key_patterns': [key_patterns]
        }
        
        url = DELETE_KETTLE_CACHE_API

        response = ApiUtilities.generate_delete_request(url=url, headers=headers, data=payload)

        if 'error_message' in response:
            error_logger.error("got error in response while sending delete to /cache \
                                | response = %s", str(response))
            return {'error_message': 'error deleting cache ' + response['error_message']}
        
        return response
