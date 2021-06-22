from ..utility.request_utilities import RequestUtilities


class IpUtilities:

    @staticmethod
    def get_ip(request) -> str:

        x_forwarded_for = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = RequestUtilities.get_parameter_from_headers(request, 'REMOTE_ADDR')

        return ip
