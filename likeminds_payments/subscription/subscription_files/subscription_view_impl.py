from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes

from ..mixins import TransactionMixin
from ..subscription_files.subscription_impl import SubscriptionImpl
from ..subscription_files.subscription_view_helper import SubscriptionViewHelper


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
