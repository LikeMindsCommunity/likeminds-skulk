class SubscriptionViewHelper:

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
