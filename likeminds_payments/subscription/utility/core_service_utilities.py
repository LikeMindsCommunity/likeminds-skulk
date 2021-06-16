from ..subscription_files.constants import member_state_api, community_questions_api
from ..utility.api_utilities import ApiUtilities
from ..utility.number_utilities import NumberUtilities


class CoreServiceUtilities:

    @staticmethod
    def is_owner(community_id: str, member_id: str) -> dict:

        if not community_id or not member_id:
            return {'error_message': 'send community_id and user_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(member_id)

        url = member_state_api
        query_params = {
            'community_id': community_id,
            'member_id': member_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        return {'is_owner': response['member']['is_owner']}

    @staticmethod
    def verify_aj(community_id: str, user_id: str, aj: str):

        community_id = NumberUtilities.get_integer_from_string(community_id)
        user_id = NumberUtilities.get_integer_from_string(user_id)
        aj = NumberUtilities.get_integer_from_string(aj)

        if not community_id or not user_id or not aj:
            return {'error_message': 'insufficient values sent'}

        url = community_questions_api
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

        return {'aj_expired': response['aj_expired']}

    @staticmethod
    def is_pending_member(community_id: str, user_id: str):

        if not community_id or not user_id:
            return {'error_message': 'send community_id and user_id'}

        community_id = NumberUtilities.get_integer_from_string(community_id)
        member_id = NumberUtilities.get_integer_from_string(user_id)

        url = member_state_api
        query_params = {
            'community_id': community_id,
            'member_id': member_id
        }
        response = ApiUtilities.generate_get_request(url=url, query_params=query_params)

        if 'error_message' in response:
            return {'error_message': 'error getting member state'}

        if response['state'] == 3:
            return {'is_pending_member': True}

        return {'is_pending_member': False}

