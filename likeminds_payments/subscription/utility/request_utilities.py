import json
from .constants import *
from .number_utilities import NumberUtilities


class RequestUtilities:

    @staticmethod
    def load_request_body(request):
        try:
            request_body = json.loads(request.body)
        except Exception as e:
            request_body = {}

        return request_body

    @staticmethod
    def fetch_request_query_params(request):

        query_param_body = {}

        for param in request.query_params:
            query_param_body[param] = request.GET.get(param)

        return query_param_body

    @staticmethod
    def get_parameter_from_headers(request, parameter) -> str:
        return request.META.get(parameter, '')

    @staticmethod
    def get_ip(request) -> str:

        x_forwarded_for = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = RequestUtilities.get_parameter_from_headers(request, 'REMOTE_ADDR')

        return ip

    @staticmethod
    def verify_growth_authentication(x_username, x_password) -> bool:

        if x_username == CMS_USER_NAME and x_password == CMS_PASSWORD:
            return True

        return False

    @staticmethod
    def get_page_number(request, key: str = "page", default: int = 1) -> int:
        return NumberUtilities.get_integer_from_string(request.GET.get(key, default))

    @staticmethod
    def get_page_size(request, key: str = "page_size", default: int = 50) -> int:
        return NumberUtilities.get_integer_from_string(request.GET.get(key, default))
