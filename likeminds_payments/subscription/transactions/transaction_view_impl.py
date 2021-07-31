from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from .transaction_impl import TransactionImpl
from .transaction_view_helper import TransactionViewHelper


class CreateTransactionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateTransactionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        validated_request_body = TransactionViewHelper.create_transaction_body_validator(request_body)
        razorpay_signature = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_RAZORPAY_SIGNATURE')

        raw_body = request.body

        if not razorpay_signature or 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': 'invalid request body or signature'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        transaction_manager = TransactionImpl(transaction_body=validated_request_body, transaction_raw_body=raw_body,
                                              transaction_signature=razorpay_signature)
        response_data = transaction_manager.create_transaction()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class FetchTransactionsView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FetchTransactionsView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = TransactionViewHelper.get_transactions_body_validator(request_body, member_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = TransactionViewHelper.get_transactions_instance_authenticator(
            validated_request_body['community_id'], member_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        transaction_manager = TransactionImpl(user_id=validated_request_body['user_id'],
                                              community_id=validated_request_body['community_id'])
        response_data = transaction_manager.fetch_transactions(page=validated_request_body['page'])

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True, 'transactions': response_data['transactions']},
            status=status_codes.HTTP_200_OK
        )


class RefundTransactionView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RefundTransactionView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = TransactionViewHelper.refund_transaction_body_validator(request_body, user_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = TransactionViewHelper.refund_transaction_instance_authenticator(
            validated_request_body['transaction_id'], user_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        transaction_manager = TransactionImpl(transaction_instance=instance_data['transaction_instance'])
        response_data = transaction_manager.refund_transaction()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class ValidateEventTransactionView(TransactionMixin, APIView):

    def get(self, request, *args, **kwargs):

        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        chatroom_id = request.GET.get('chatroom_id')

        request_validated = self.validate_request_params(user_id, chatroom_id)

        if not request_validated:
            return JsonResponse(request_validated, status=status_codes.HTTP_400_BAD_REQUEST)

        transaction_manager = TransactionImpl()

        response_data = transaction_manager.valid_event_transaction(chatroom_id, user_id)

        if response_data.get('error_message'):
            return JsonResponse(response_data, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse(response_data)

    def validate_request_params(self, user_id, chatroom_id):

        if not user_id:
            return {'error_message': "In-valid user id"}

        if not chatroom_id:
            return {'error_message': "In-valid chatroom id"}

        return {}

