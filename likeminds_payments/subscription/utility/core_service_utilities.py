from ..orders.constants import *
from .constants import *
from ..utility.api_utilities import ApiUtilities
from ..utility.number_utilities import NumberUtilities


class CoreServiceUtilities:

    @staticmethod
    def has_permission(community_id: str, member_id: str) -> dict:

        if not community_id or not member_id:
            return {'error_message': 'send community_id and user_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(member_id)

        url = MEMBER_STATE_API
        query_params = {
            'community_id': community_id,
            'member_id': member_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        if 'state' not in response:
            return {'error_message': 'no state field in member state response'}

        output = {'has_permission': False}

        if response['state'] == ADMIN:
            return {'has_permission': True}

        return output

    @staticmethod
    def verify_aj(community_id: str, user_id: str, aj: str):

        community_id = NumberUtilities.get_integer_from_string(community_id)
        user_id = NumberUtilities.get_integer_from_string(user_id)
        aj = NumberUtilities.get_integer_from_string(aj)

        if not community_id or not user_id or not aj:
            return {'error_message': 'insufficient values sent'}

        url = COMMUNITY_QUESTIONS_API
        query_params = {
            'community_id': community_id,
            'aj': aj
        }
        headers = {
            'x-member-id': '{}'.format(user_id)
        }

        response = ApiUtilities.generate_get_request(url=url, headers=headers, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        if 'aj_expired' not in response:
            return {'error_message': 'no aj_expired field in member_state'}

        return {'aj_expired': response['aj_expired']}

    @staticmethod
    def is_pending_member(community_id: str, user_id: str):

        if not community_id or not user_id:
            return {'error_message': 'send community_id and user_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(user_id)

        url = MEMBER_STATE_API
        query_params = {
            'community_id': community_id,
            'member_id': member_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        if 'state' not in response:
            return {'error_message': 'no state field in member state response'}

        if response['state'] == PENDING_MEMBER:
            return {'is_pending_member': True}

        return {'is_pending_member': False}

    @staticmethod
    def get_community_data(community_id: str):

        if not community_id:
            return {'error_message': 'send community_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)

        url = COMMUNITY_API
        query_params = {
            'community_id': community_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        if 'community' not in response:
            return {'error_message': 'no community object in community data response'}

        return {'community': response['community']}

    @staticmethod
    def remove_member(community_id: str, member_id: str):

        if not community_id:
            return {'error_message': 'send community_id'}

        if not member_id:
            return {'error_message': 'send member_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(member_id)

        url = REMOVE_MEMBER_API
        data = {
            'community_id': community_id,
            'member_id': member_id
        }

        response = ApiUtilities.generate_post_request(url=url, data=data)

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        if 'success' not in response:
            return {'error_message': 'invalid response from remove member api'}

        return {'success': response['success']}

    @staticmethod
    def edit_community(community_id: str, member_id: str):

        if not community_id:
            return {'error_message': 'send community_id'}

        if not member_id:
            return {'error_message': 'send member_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(member_id)

        url = EDIT_COMMUNITY_API
        data = {
            'community_id': community_id,
            'is_paid': True
        }
        headers = {
            'x-member-id': '{}'.format(member_id)
        }

        response = ApiUtilities.generate_post_request(url=url, data=data, headers=headers)

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        if 'success' not in response:
            return {'error_message': 'invalid response from remove member api'}

        return {'success': response['success']}

    @staticmethod
    def get_all_members(community_id: str, member_id: str, page: int):

        if not community_id:
            return {'error_message': 'send community_id'}

        if not member_id:
            return {'error_message': 'send member_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(member_id)

        url = ALL_MEMBERS_API
        query_params = {
            'community_id': community_id,
            'page': page
        }
        headers = {
            'x-member-id': '{}'.format(member_id),
            'x-platform-code': 'web'
        }

        response = ApiUtilities.generate_get_request(url=url, query_params=query_params, headers=headers)

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        if 'members' not in response:
            return {'error_message': 'invalid response from remove member api'}

        return {'members': response['members']}
