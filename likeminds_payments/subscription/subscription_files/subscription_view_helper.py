import subscription.subscription_files.constants as constants


class SubscriptionViewHelper:

    @staticmethod
    def create_order_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in request_body or not request_body['plan_id']:
            return {'error_message': 'send plan_id'}

        if 'payment_page_url' not in request_body or not request_body['payment_page_url']:
            return {'error_message': 'send payment_page_url'}

        return request_body

    @staticmethod
    def verify_order_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'order_id' not in request_body or not request_body['order_id']:
            return {'error_message': 'send order_id'}

        if 'razorpay_order_id' not in request_body or not request_body['razorpay_order_id']:
            return {'error_message': 'send razorpay_order_id'}

        if 'razorpay_payment_id' not in request_body or not request_body['razorpay_payment_id']:
            return {'error_message': 'send razorpay_payment_id'}

        if 'razorpay_signature' not in request_body or not request_body['razorpay_signature']:
            return {'error_message': 'send razorpay_signature'}

        return request_body

    @staticmethod
    def create_transaction_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'event' not in request_body or request_body['event'] not in constants.VALID_WEBHOOK_EVENTS:
            return {'error_message': 'invalid event recognized'}

        if 'payload' not in request_body or not request_body['payload']:
            return {'error_message': 'no payload detected'}

        if request_body['event'] == constants.VALID_WEBHOOK_EVENTS[0]:
            if 'refund' not in request_body['payload'] or not request_body['payload']['refund']:
                return {'error_message': 'no refund object detected'}

        if 'payment' not in request_body['payload'] or not request_body['payload']['payment']:
            return {'error_message': 'no payment object detected'}

        if 'entity' not in request_body['payload']['payment'] or not request_body['payload']['payment']['entity']:
            return {'error_message': 'no entity object detected'}

        return request_body

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
