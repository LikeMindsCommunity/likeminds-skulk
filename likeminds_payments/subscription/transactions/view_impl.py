from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from .impl import TransactionImpl
from .view_helper import TransactionViewHelper


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
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )