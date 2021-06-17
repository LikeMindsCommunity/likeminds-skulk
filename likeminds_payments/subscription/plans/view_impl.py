from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..mixins import TransactionMixin
from ..utility.request_utilities import RequestUtilities
from ..plans.impl import PlanImpl
from ..plans.view_helper import PlanViewHelper


class CreatePlanView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreatePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        plan_body = RequestUtilities.load_request_body(request)

        validated_request_body = PlanViewHelper.create_plan_body_validator(plan_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = PlanViewHelper.create_plan_instance_helper(validated_request_body)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = PlanImpl(plan_instance=instance_data['plan_instance'])
        response_data = subscription_manager.create_plan()

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

        query_params = PlanViewHelper.get_plan_filter_params(request)

        if 'error_message' in query_params:
            return JsonResponse(
                {'success': False, 'error_message': query_params['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = PlanImpl(community_id=query_params['community_id'])
        response_data = subscription_manager.fetch_plan()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True, 'plans': response_data['plans']},
            status=status_codes.HTTP_200_OK
        )


class DeletePlanView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = PlanViewHelper.delete_plan_body_validator(request_body)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        subscription_manager = PlanImpl(plan_id=validated_request_body['plan_id'])
        response_data = subscription_manager.delete_plan()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )