from subscription.search.constants import SUBSCRIPTION_PLAN_SUB_TITLE_FIELD, SUBSCRIPTION_PLAN_FIELDS_DICTIONARY_MAPPING


class SearchViewHelper:

    @staticmethod
    def get_validated_query_params(request):
        query_params = {
            'community_id': None,
            'search': None
        }

        if not request.GET.get('community_id'):
            return {'error_message': "Invalid community_id"}

        query_params['community_id'] = request.GET.get('community_id')

        if not request.GET.get('search'):
            return {'error_message': "Invalid search"}

        query_params['search'] = request.GET.get('search')
        query_params['search_field'] = request.GET.get('search_field', SUBSCRIPTION_PLAN_SUB_TITLE_FIELD)

        if query_params['search_field'].lower() not in SUBSCRIPTION_PLAN_FIELDS_DICTIONARY_MAPPING:
            return {"error_message": "Invalid Search Type"}

        return query_params
