from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..mixins import TransactionMixin
from ..utility.json_utilities import JsonUtilities
from ..utility.request_utilities import RequestUtilities
from ..plans.plan_impl import PlanImpl
from ..plans.plan_view_helper import PlanViewHelper


class CreatePlanView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreatePlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        plan_body = RequestUtilities.load_request_body(request)
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = PlanViewHelper.create_plan_body_validator(plan_body, user_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = PlanViewHelper.create_plan_instance_helper(validated_request_body, user_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        plan_manager = PlanImpl(plan_instance=instance_data['plan_instance'])
        response_data = plan_manager.create_plan()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
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

        plan_manager = PlanImpl(community_id=query_params['community_id'])
        response_data = plan_manager.fetch_plan()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
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
        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = PlanViewHelper.delete_plan_body_validator(request_body, user_id)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        instance_data = PlanViewHelper.delete_plan_instance_helper(validated_request_body, user_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        plan_manager = PlanImpl(plan_instance=instance_data['plan_instance'])
        response_data = plan_manager.delete_plan()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class CreateEventPlanView(TransactionMixin, APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateEventPlanView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        if not request_body:
            return JsonResponse({'success': False, 'error_message': "Invalid request"})

        plan_manager = PlanImpl()

        response_data = plan_manager.create_event_plan(request_body)

        if response_data.get('error_message'):

            return JsonResponse(response_data, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse(response_data)


class FetchEventPlanView(TransactionMixin, APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        chatroom_ids = JsonUtilities.load_json(request.GET.get('chatroom_ids'))

        if not chatroom_ids:
            return JsonResponse({'error_message': "In-valid chatroom ids"}, status=status_codes.HTTP_400_BAD_REQUEST)

        plan_manager = PlanImpl()

        response_data = plan_manager.fetch_event_plan(chatroom_ids)

        if response_data.get('error_message'):
            return JsonResponse(response_data, status=status_codes.HTTP_400_BAD_REQUEST)

        return JsonResponse(response_data)
