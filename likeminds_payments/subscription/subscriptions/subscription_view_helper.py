from .constants import *
from ..utility.time_utilities import TimeUtilities
from ..utility.number_utilities import NumberUtilities
import json


class SubscriptionViewHelper:

    @staticmethod
    def create_subscription_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        validated_request_body = {
            'payment_id': None,
            'community_id': None,
            'type': None,
            'user_id': None,
            'valid_till': None,
            'n_days': None,
            'shared_by': None
        }

        if 'payment_id' not in request_body or not request_body['payment_id']:

            if 'community_id' in request_body:

                validated_request_body['community_id'] = request_body['community_id']

                if 'type' not in request_body or not request_body['type'] in [FREE_SUBSCRIPTION, DASHBOARD, PAID]:
                    return {'error_message': 'invalid type value'}

                validated_request_body['type'] = request_body['type']

                if 'user_id' in request_body:
                    validated_request_body['user_id'] = request_body['user_id']

                if 'shared_by' in request_body:
                    validated_request_body['shared_by'] = request_body['shared_by']

                if 'valid_till' in request_body:
                    current_time = TimeUtilities.current_time_in_milliseconds()
                    if NumberUtilities.get_integer_from_string(request_body['valid_till'] < current_time):
                        return {'error_message': 'send valid date in future'}
                    validated_request_body['valid_till'] = request_body['valid_till']

                if 'n_days' in request_body:
                    if request_body['n_days'] < 0:
                        return {'error_message': 'send valid n_days'}
                    validated_request_body['n_days'] = request_body['n_days']

            else:
                return {'error_message': 'send payment_id'}

        else:
            validated_request_body['payment_id'] = request_body['payment_id']

        return validated_request_body

    @staticmethod
    def start_subscription_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'user_id' not in request_body or not request_body['user_id']:
            return {'error_message': 'send user_id'}

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id'}

        return request_body

    @staticmethod
    def get_subscription_filter_params(request):

        query_params = {
            'community_id': None,
            'member_ids': None
        }

        if request.GET.get('community_id'):
            query_params['community_id'] = request.GET.get('community_id')

        if request.GET.get('member_ids'):
            query_params['member_ids'] = json.loads(request.GET.get('member_ids'))

        return query_params

    @staticmethod
    def cancel_subscription_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        body = {
            'community_id': None,
            'user_id': None
        }

        if 'community_id' not in request_body:
            return {'error_message': 'send community_id'}

        body['community_id'] = request_body['community_id']

        if 'user_id' in request_body:
            body['user_id'] = request_body['user_id']

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        return body

    @staticmethod
    def get_community_meta_filter_params(request):

        query_params = {}

        if request.GET.get('payment_id'):
            query_params['payment_id'] = request.GET.get('payment_id')

        else:
            return {'error_message': 'send payment_id in query params'}

        return query_params

    @staticmethod
    def convert_to_paid_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id'}

        return request_body

    @staticmethod
    def external_migration_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'members_data_url' not in request_body or not request_body['members_data_url']:
            return {'error_message': 'send members_data_url in body'}

        return request_body
