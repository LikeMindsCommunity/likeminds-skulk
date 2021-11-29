from subscription.search.constants import SUBSCRIPTION_PLAN_SUB_TITLE_FIELD


class SearchViewHelper:

    @staticmethod
    def get_validated_query_params(request):
        query_params = {
            'community_id': None,
            'search': None
        }

        if not request.GET.get('community_id'):
            return {'error_message': "Invalid Community ID"}

        query_params['community_id'] = request.GET.get('community_id')

        if not request.GET.get('search'):
            return {'error_message': "Invalid Search Term"}

        query_params['search'] = request.GET.get('search')
        query_params['search_field'] = request.GET.get('search_field', SUBSCRIPTION_PLAN_SUB_TITLE_FIELD)

        return query_params
