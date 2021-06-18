from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from .impl import SubscriptionHistoryImpl
from .view_helper import SubscriptionHistoryViewHelper


class FetchSubscriptionHistoryView(TransactionMixin, APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionHistoryViewHelper.get_subscription_history_filter_params(request)
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if 'error_message' in query_params:
            return JsonResponse(
                {'success': False, 'error_message': query_params['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        if not user_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send x-member-id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionHistoryImpl(user_id=user_id, community_id=query_params['community_id'])
        response_data = subscription_manager.fetch_subscription_history()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'subscription_history': response_data['histories']},
            status=status_codes.HTTP_200_OK
        )