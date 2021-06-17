from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from .impl import OrderImpl
from .view_helper import OrderViewHelper


class CreateOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateOrderView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = OrderViewHelper.create_order_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        order_instance = OrderViewHelper.create_order_instance_helper(validated_request_body)

        if 'error_message' in order_instance:
            return {'error_message': order_instance['error_message']}

        order_manager = OrderImpl(order_instance=order_instance['order_instance'])
        response_data = order_manager.create_order()

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

        validated_request_body = OrderViewHelper.verify_order_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        order_manager = OrderImpl(razorpay_order_id=validated_request_body['razorpay_order_id'],
                                  razorpay_payment_id=validated_request_body['razorpay_payment_id'],
                                  razorpay_signature=validated_request_body['razorpay_signature'])
        response_data = order_manager.verify_order()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )
