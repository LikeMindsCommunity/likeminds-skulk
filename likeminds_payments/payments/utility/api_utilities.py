import requests
from requests.exceptions import HTTPError


class ApiUtilities:

    @staticmethod
    def generate_get_request(url, headers={}, query_params={}):

        if not url:
            return {'error_message': 'send url'}

        response = requests.get(url=url, params=query_params, headers=headers)

        validated_response = ApiUtilities.validate_response(response)

        return validated_response

    @staticmethod
    def generate_post_request(url, headers={}, data={}):

        if not url:
            return {'error_message': 'send url'}

        response = requests.post(url=url, data=data, headers=headers)

        validated_response = ApiUtilities.validate_response(response)

        return validated_response

    @staticmethod
    def validate_response(response):

        if response.status_code == 200:
            return response.json()

        else:
            return {'error_message': 'error while making request'}
