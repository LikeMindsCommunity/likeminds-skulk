from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from ..subscription.subscription_impl import SubscriptionImpl
from ..subscription.constants import subscription_plan_choices


class CreatePlanView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreatePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        plan_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.create_plan_body_validator(plan_body)

        if 'error_message' in validated_request_body:
            return JsonResponse({'success': False, 'error_message': validated_request_body['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.create_plan(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse({'success': False, 'error_message': response_data['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True, 'url': response_data['url']}, status=status_codes.HTTP_200_OK)


class FetchPlanView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SubscriptionViewHelper.get_plan_filter_params(request)

        if 'error_message' in query_params:
            return JsonResponse({'success': False, 'error_message': query_params['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.fetch_plan(query_params['community_id'])

        if 'error_message' in response_data:
            return JsonResponse({'success': False, 'error_message': response_data['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True, 'plans': response_data}, status=status_codes.HTTP_200_OK)


class DeletePlanView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.delete_plan_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse({'success': False, 'error_message': validated_request_body['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.delete_plan(validated_request_body['plan_id'])

        if 'error_message' in response_data:
            return JsonResponse({'success': False, 'error_message': response_data['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True}, status=status_codes.HTTP_200_OK)


class CreateOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateOrderView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.create_order_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse({'success': False, 'error_message': validated_request_body['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.create_order(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse({'success': False, 'error_message': response_data['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True, "order": response_data}, status=status_codes.HTTP_200_OK)


class VerifyOrderView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(VerifyOrderView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = SubscriptionViewHelper.verify_order_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse({'success': False, 'error_message': validated_request_body['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        subscription_manager = SubscriptionImpl()
        response_data = subscription_manager.verify_order(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse({'success': False, 'error_message': response_data['error_message']}, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True}, status=status_codes.HTTP_200_OK)


class SubscriptionViewHelper:

    @staticmethod
    def create_plan_body_validator(plan_body):

        if not plan_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in plan_body or not plan_body['plan_id']:
        
            if 'community_id' not in plan_body or not plan_body['community_id']:
                return {'error_message': 'send community_id'}
            
            if 'duration_name' not in plan_body or not plan_body['duration_name']:
                return {'error_message': 'send duration_name of plan'}

            if plan_body['duration_name'] not in subscription_plan_choices:
                return {'error_message': 'invalid duration_name'}

        else:

            if 'community_id' in plan_body:
                return {'error_message': 'community_id cannot be updated'}

            if 'duration_name' in plan_body:
                return {'error_message': 'duration_name cannot be updated'}
        
        if 'cost' not in plan_body or not plan_body['cost']:
            return {'error_message': 'send cost of plan'}

        if plan_body['cost'] == 0:
            return {'error_message': 'cost of plan cannot be zero'}

        if 'cm_emails' not in plan_body or not plan_body['cm_emails']:
            return {'error_message': 'send cm_emails'}

        if 'buddy_emails' not in plan_body or not plan_body['buddy_emails']:
            return {'error_message': 'send buddy_emails'}

        return plan_body

    @staticmethod
    def get_plan_filter_params(request):

        query_params = {}

        if request.GET.get('community_id'):
            query_params['community_id'] = request.GET.get('community_id')

        else:
            return {'error_message': 'send community_id in query params'}

        return query_params

    @staticmethod
    def delete_plan_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in request_body or not request_body['plan_id']:
            return {'error_message': 'send plan_id'}

        return request_body

    @staticmethod
    def create_order_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in request_body or not request_body['plan_id']:
            return {'error_message': 'send plan_id'}

        if 'payment_page_url' not in request_body or not request_body['payment_page_url']:
            return {'error_message': 'send payment_page_url'}

        return request_body

    @staticmethod
    def verify_order_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'order_id' not in request_body or not request_body['order_id']:
            return {'error_message': 'send order_id'}

        if 'razorpay_order_id' not in request_body or not request_body['razorpay_order_id']:
            return {'error_message': 'send razorpay_order_id'}

        if 'razorpay_payment_id' not in request_body or not request_body['razorpay_payment_id']:
            return {'error_message': 'send razorpay_payment_id'}

        if 'razorpay_signature' not in request_body or not request_body['razorpay_signature']:
            return {'error_message': 'send razorpay_signature'}

        return request_body
