
from .constants import *
from ..utility.api_utilities import ApiUtilities


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
            return {'error_message': 'error deleting cache' + response['error_message']}
        
        return response
