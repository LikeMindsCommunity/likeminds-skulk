from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from ..payment_page.payment_page_impl import PaymentPageImpl
from ..payment_page.payment_page_view_helper import PaymentPageViewHelper


class CreatePaymentPageView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreatePaymentPageView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        payment_page_body = RequestUtilities.load_request_body(request)
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = PaymentPageViewHelper.create_payment_page_body_validator(payment_page_body, user_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = PaymentPageViewHelper.create_payment_page_instance_helper(validated_request_body, user_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class UpdatePaymentPageView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdatePaymentPageView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        payment_page_body = RequestUtilities.load_request_body(request)
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = PaymentPageViewHelper.update_payment_page_body_validator(payment_page_body, user_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = PaymentPageViewHelper.update_payment_page_instance_helper(validated_request_body, user_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )
