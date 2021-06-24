from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from .subscription_impl import SubscriptionImpl
from .subscription_view_helper import SubscriptionViewHelper


class CreateSubscriptionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateSubscriptionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = SubscriptionViewHelper.create_subscription_body_validator(request_body, member_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl(payment_id=validated_request_body['payment_id'],
                                                community_id=validated_request_body['community_id'],
                                                member_id=member_id, subscription_type=validated_request_body['type'],
                                                user_id=validated_request_body['user_id'])
        response_data = subscription_manager.create_subscription(valid_till=validated_request_body['valid_till'],
                                                                 n_days=validated_request_body['n_days'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class StartSubscriptionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StartSubscriptionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        validated_request_body = SubscriptionViewHelper.start_subscription_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl(member_id=validated_request_body['user_id'],
                                                community_id=validated_request_body['community_id'])
        response_data = subscription_manager.start_subscription()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class FetchSubscriptionView(TransactionMixin, APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionViewHelper.get_subscription_filter_params(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if 'error_message' in query_params:
            return JsonResponse(
                {'success': False, 'error_message': query_params['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        if not member_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send x-member-id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl(member_id=member_id, community_id=query_params['community_id'])
        response_data = subscription_manager.fetch_subscription(member_ids=query_params['member_ids'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True, 'subscriptions': response_data['subscriptions']},
            status=status_codes.HTTP_200_OK
        )


class CancelSubscriptionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CancelSubscriptionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = SubscriptionViewHelper.cancel_subscription_body_validator(request_body, member_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl(member_id=member_id,
                                                community_id=validated_request_body['community_id'],
                                                user_id=validated_request_body['user_id'])
        response_data = subscription_manager.cancel_subscription()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
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

        subscription_manager = SubscriptionImpl(payment_id=query_params['payment_id'])
        response_data = subscription_manager.fetch_community_meta()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True, 'community_id': response_data['community_id']},
            status=status_codes.HTTP_200_OK
        )
