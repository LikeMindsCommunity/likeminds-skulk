from .response_utilities import ResponseUtilities
from .core_service_utilities import CoreServiceUtilities

from rest_framework import status as status_codes


class AuthenticationUtilities:

    @staticmethod
    def has_permission(member_id, community_id) -> dict:

        if not member_id or not community_id:
            return ResponseUtilities.get_impl_error_context("send member_id and community_id",
                                                            status_codes.HTTP_400_BAD_REQUEST)

        has_permission_check = CoreServiceUtilities.has_permission(community_id, member_id)

        if 'error_message' in has_permission_check:
            return ResponseUtilities.get_impl_error_context(has_permission_check['error_message'],
                                                            status_codes.HTTP_502_BAD_GATEWAY)

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return ResponseUtilities.get_impl_error_context('You are not the Owner/CM of the community',
                                                            status_codes.HTTP_401_UNAUTHORIZED)

        return {'success': True}
