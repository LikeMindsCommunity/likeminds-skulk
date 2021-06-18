from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from ..subscription_files.subscription_impl import SubscriptionImpl
from ..subscription_files.subscription_view_helper import SubscriptionViewHelper


class FetchSubscriptionHistoryView(TransactionMixin, APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionViewHelper.get_subscription_history_filter_params(request)
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

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.fetch_subscription_history(user_id, query_params['community_id'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'subscription_history': response_data},
            status=status_codes.HTTP_200_OK
        )


class FetchCommunityMetaView(TransactionMixin, APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionViewHelper.get_community_meta_filter_params(request)

        if 'error_message' in query_params:
            return JsonResponse(
                {'success': False, 'error_message': query_params['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.fetch_community_meta(query_params['payment_id'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'community_id': response_data['community_id']},
            status=status_codes.HTTP_200_OK
        )
