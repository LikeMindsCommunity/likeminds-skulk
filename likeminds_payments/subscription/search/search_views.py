from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework import status as status_codes

from .search_impl import SearchImpl
from .search_view_helper import SearchViewHelper

from ..utility.request_utilities import RequestUtilities
from ..utility.response_utilities import ResponseUtilities

# ------------  do not remove this import ------------------
# Reason: whenever we create any document for indexing, elasticsearch can not detect document without this import.
from .subscription_plan_index import SubscriptionPlanDocument
from .subscription_history_index import SubscriptionHistoryDocument


# ----------------------------------------------------------


class SearchView(APIView):

    def get(self, request, *args, **kwargs):
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        page = RequestUtilities.get_page_number(request)
        page_size = RequestUtilities.get_page_size(request)

        if not member_id:
            response = ResponseUtilities.get_error_context(success=False, error_message="Invalid member_id in headers")
            return JsonResponse(response, status=status_codes.HTTP_403_FORBIDDEN)

        query_params = SearchViewHelper.get_validated_query_params(request)

        if query_params.get('error_message'):
            response = ResponseUtilities.get_error_context(success=False,
                                                           error_message=query_params.get('error_message'))
            return JsonResponse(response, status=status_codes.HTTP_400_BAD_REQUEST)

        search_manager = SearchImpl(member_id=member_id, search_term=query_params.get('search'),
                                    search_field=query_params.get('search_field'),
                                    page=page, page_size=page_size, community_id=query_params.get('community_id'))

        data = search_manager.search_plan()

        response = {
            'success': True,
            'data': data
        }

        return JsonResponse(response, status=status_codes.HTTP_200_OK)


class SearchHistoryView(APIView):

    def get(self, request, *args, **kwargs):
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        page = RequestUtilities.get_page_number(request)
        page_size = RequestUtilities.get_page_size(request)

        if not member_id:
            response = ResponseUtilities.get_error_context(success=False, error_message="Invalid member_id in headers")
            return JsonResponse(response, status=status_codes.HTTP_403_FORBIDDEN)

        query_params = SearchViewHelper.get_validated_query_params(request)

        if query_params.get('error_message'):
            response = ResponseUtilities.get_error_context(success=False,
                                                           error_message=query_params.get('error_message'))
            return JsonResponse(response, status=status_codes.HTTP_400_BAD_REQUEST)

        search_manager = SearchImpl(member_id=member_id, search_term=query_params.get('search'),
                                    search_field=query_params.get('search_field'),
                                    page=page, page_size=page_size, community_id=query_params.get('community_id'))

        filtered_member_ids = search_manager.search_history()

        response = {
            'success': True,
            'filtered_member_ids': filtered_member_ids
        }

        return JsonResponse(response, status=status_codes.HTTP_200_OK)

