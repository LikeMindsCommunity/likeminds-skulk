from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from ..orders.orders_impl import OrdersImpl

class CreateOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateOrderView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        
        request_body = RequestUtilities.load_request_body(request)

        if not request_body:
            return JsonResponse({'error_message': "Invalid request body"}, status=status_codes.HTTP_400_BAD_REQUEST)

        if 'planId' not in request_body or not request_body['planId']:
            return JsonResponse({'error_message': "send plan id"}, status=status_codes.HTTP_400_BAD_REQUEST)

        orders_manager = OrdersImpl()
        orders_context = orders_manager.create_order(request_body['planId'])

        if 'error_message' in orders_context:
            return JsonResponse({'error_message': orders_context['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse(orders_context, status=status_codes.HTTP_200_OK)

class VerifyOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(VerifyOrderView, self).dispatch(request, *args, **kwargs)

    def post(self, request, order_id, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = OrdersViewHelper.request_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse({'error_message': validated_request_body['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)        

        orders_manager = OrdersImpl()
        response_data = orders_manager.verify_order(request_body)

        if 'error_message' in response_data:
            return JsonResponse({'error_message': response_data['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse({'redirect_url': response_data['redirect_url']}, status=status_codes.HTTP_200_OK)


class OrdersViewHelper:

    def request_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}
        
        if 'razorpay_order_id' not in request_body or not request_body['razorpay_order_id']:
            return {'error_message': 'send razorpay_order_id'}
        
        if 'razorpay_payment_id' not in request_body or not request_body['razorpay_payment_id']:
            return {'error_message': 'send razorpay_payment_id'}
        
        if 'razorpay_signature' not in request_body or not request_body['razorpay_signature']:
            return {'error_message': 'send razorpay_signature'}

        if order_id != request_body['razorpay_order_id']:
            return {'error_message': 'invalid order_id in url'}

        return request_body
        