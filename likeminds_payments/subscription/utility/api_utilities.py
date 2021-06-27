import requests


class ApiUtilities:

    @staticmethod
    def generate_get_request(url, headers=None, query_params=None):

        if query_params is None:
            query_params = {}
        if headers is None:
            headers = {}

        if not url:
            return {'error_message': 'send url'}

        response = requests.get(url=url, params=query_params, headers=headers)

        validated_response = ApiUtilities.validate_response(response)

        return validated_response

    @staticmethod
    def generate_post_request(url, headers=None, data=None):

        if data is None:
            data = {}
        if headers is None:
            headers = {}

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
