import subscription.subscription_files.constants as constants


class SubscriptionViewHelper:

    @staticmethod
    def create_subscription_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'payment_id' not in request_body or not request_body['payment_id']:
            if 'community_id' in request_body:
                if 'type' not in request_body or not request_body['type'] == constants.FREE_SUBSCRIPTION:
                    return {'error_message': 'invalid type value'}

            return {'error_message': 'send payment_id'}

        return request_body

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
            'community_id': None
        }

        if request.GET.get('community_id'):
            query_params['community_id'] = request.GET.get('community_id')

        return query_params

    @staticmethod
    def get_subscription_history_filter_params(request):

        query_params = {}

        if request.GET.get('community_id'):
            query_params['community_id'] = request.GET.get('community_id')

        else:
            return {'error_message': 'send community_id in query params'}

        return query_params

    @staticmethod
    def get_community_meta_filter_params(request):

        query_params = {}

        if request.GET.get('payment_id'):
            query_params['payment_id'] = request.GET.get('payment_id')

        else:
            return {'error_message': 'send payment_id in query params'}

        return query_params
