from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from ..subscription_files.subscription_impl import SubscriptionImpl
from ..subscription_files.subscription_view_helper import SubscriptionViewHelper


class CreatePlanView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreatePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        plan_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.create_plan_body_validator(plan_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.create_plan(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'url': response_data['url']},
            status=status_codes.HTTP_200_OK
        )


class FetchPlanView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionViewHelper.get_plan_filter_params(request)

        if 'error_message' in query_params:
            return JsonResponse(
                {'success': False, 'error_message': query_params['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.fetch_plan(query_params['community_id'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'plans': response_data},
            status=status_codes.HTTP_200_OK
        )


class DeletePlanView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.delete_plan_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.delete_plan(validated_request_body['plan_id'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class CreateOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateOrderView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.create_order_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.create_order(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, "order": response_data},
            status=status_codes.HTTP_200_OK
        )


class VerifyOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(VerifyOrderView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.verify_order_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.verify_order(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class CreateTransactionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateTransactionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        validated_request_body = SubscriptionViewHelper.create_transaction_body_validator(request_body)
        razorpay_signature = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_RAZORPAY_SIGNATURE')

        raw_body = request.body

        if not razorpay_signature or 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': 'invalid request body or signature'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.create_transaction(validated_request_body, raw_body, razorpay_signature)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class CreateSubscriptionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateSubscriptionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        validated_request_body = SubscriptionViewHelper.create_subscription_body_validator(request_body)
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        if not user_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send x-member-id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.create_subscription(validated_request_body, user_id)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
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

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.start_subscription(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class FetchSubscriptionView(TransactionMixin, APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionViewHelper.get_subscription_filter_params(request)
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
        response_data = subscription_manager.fetch_subscription(user_id, query_params['community_id'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'subscriptions': response_data},
            status=status_codes.HTTP_200_OK
        )


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
