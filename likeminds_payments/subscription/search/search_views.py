from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework import status as status_codes

from .search_impl import SearchImpl
from .search_view_helper import SearchViewHelper

from ..utility.request_utilities import RequestUtilities

# ------------  do not remove this import ------------------

from .subscription_plan_index import SubscriptionPlanDocument

# ----------------------------------------------------------


class SearchView(APIView):

    def get(self, request, *args, **kwargs):
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        page = RequestUtilities.get_page_number(request)
        page_size = RequestUtilities.get_page_size(request)

        if not member_id:
            response = {'success': False, 'error_message': 'Invalid Member ID'}
            return JsonResponse(response, status=status_codes.HTTP_403_FORBIDDEN)

        query_params = SearchViewHelper.get_validated_query_params(request)

        if query_params.get('error_message'):
            response = {'success': False, 'error_message': query_params.get('error_message')}
            return JsonResponse(response, status=status_codes.HTTP_400_BAD_REQUEST)

        search_manager = SearchImpl(member_id=member_id, search_term=query_params.get('search'),
                                    search_field=query_params.get('search_field'),
                                    page=page, page_size=page_size, community_id=query_params.get('community_id'))

        plans = search_manager.search_plan()

        response = {
            'success': True,
            'plans': plans
        }

        return JsonResponse(response, status=status_codes.HTTP_200_OK)
