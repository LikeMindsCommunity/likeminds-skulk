from .constants import *
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
            'aj': None,
            'type': None,
            'user_id': None,
            'valid_till': None,
            'n_days': None
        }

        if 'payment_id' not in request_body or not request_body['payment_id']:

            if 'community_id' in request_body:

                validated_request_body['community_id'] = request_body['community_id']

                if 'type' not in request_body or not request_body['type'] in [FREE_SUBSCRIPTION, DASHBOARD]:
                    return {'error_message': 'invalid type value'}

                if 'user_id' not in request_body or not request_body['user_id']:
                    return {'error_message': 'send user_id'}

                validated_request_body['type'] = request_body['type']
                validated_request_body['user_id'] = request_body['user_id']

                if 'aj' in request_body:
                    validated_request_body['aj'] = request_body['aj']

                if 'valid_till' in request_body:
                    validated_request_body['valid_till'] = request_body['valid_till']

                if 'n_days' in request_body:
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

        if 'community_id' not in request_body:
            return {'error_message': 'send community_id'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        return request_body

    @staticmethod
    def get_community_meta_filter_params(request):

        query_params = {}

        if request.GET.get('payment_id'):
            query_params['payment_id'] = request.GET.get('payment_id')

        else:
            return {'error_message': 'send payment_id in query params'}

        return query_params
