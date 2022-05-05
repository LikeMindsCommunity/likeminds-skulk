from django.utils.deprecation import MiddlewareMixin
from ..utility.core_service_utilities import CoreServiceUtilities


class CustomAuthenticateUserIDMiddleware(MiddlewareMixin):

    def process_request(self, request: {}) -> None:

        if request.META.get('HTTP_X_MEMBER_ID'):
            user_object = CoreServiceUtilities.get_user_details({'member_id': request.META.get('HTTP_X_MEMBER_ID')})

            if 'error_message' not in user_object:
                request.META['HTTP_X_MEMBER_ID'] = user_object.get('user')['id']
