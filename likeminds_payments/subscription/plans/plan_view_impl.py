from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .plan_helper import PlanHelper
from .serializers import PlanSerializer
from ..mixins import TransactionMixin
from ..search.sync import ElasticSearchSync
from ..utility.json_utilities import JsonUtilities
from ..utility.request_utilities import RequestUtilities
from ..utility.response_utilities import ResponseUtilities
from ..plans.plan_impl import PlanImpl
from ..plans.constants import *
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

        if validated_request_body.get('plan_id'):
            analytics_event_name = EDIT_PLAN_ANALYTICS_EVENT_NAME

        else:
            analytics_event_name = CREATE_PLAN_ANALYTICS_EVENT_NAME

        instance_data = PlanViewHelper.create_plan_instance_helper(validated_request_body, user_id)

        if 'error_message' in instance_data:
            return JsonResponse(
                {'success': False, 'error_message': instance_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        serialized_plan = PlanSerializer(instance_data['plan_instance'])
        plan_title_context = PlanHelper.get_plan_title_and_subtitle_for_plan(plan_object=serialized_plan,
                                                                             plan_instance=instance_data['plan_instance'])
        serialized_plan.update(plan_title_context)

        # Add Event Analytics
        PlanViewHelper.add_event_for_membership_plan(serialized_plan, analytics_event_name, user_id)

        # Creating Subscription Plan Cohort
        cohort_response = PlanViewHelper.create_subscription_plan_cohort(serialized_plan, user_id)

        if 'error_message' in cohort_response:
            return JsonResponse(
                {'success': False, 'error_message': cohort_response['error_message']},
                status=cohort_response['status_code']
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
        response_data = plan_manager.fetch_plan(plan_id=query_params['plan_id'],
                                                renew=query_params['renew'],
                                                free=query_params['free'])

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

        # Add Event Analytics
        serialized_plan = PlanSerializer(instance_data['plan_instance'])
        plan_title_context = PlanHelper.get_plan_title_and_subtitle_for_plan(plan_object=serialized_plan,
                                                                             plan_instance=instance_data['plan_instance'])
        serialized_plan.update(plan_title_context)
        PlanViewHelper.add_event_for_membership_plan(serialized_plan, DELETE_PLAN_ANALYTICS_EVENT_NAME, user_id)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        ElasticSearchSync.delete_subscription_plan(validated_request_body.get('plan_id'))

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class CreateEventPlanView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateEventPlanView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        validated_request = PlanViewHelper.validate_request_body_for_create_event_plan_view(request_body)

        if validated_request.get('error_message'):
            return JsonResponse(validated_request, status=status_codes.HTTP_400_BAD_REQUEST)

        plan_manager = PlanImpl()

        try:
            response_data = plan_manager.create_event_plan(request_body, member_id)

        except Exception as e:

            return JsonResponse({'error_message': e.args}, status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(response_data)


class FetchEventPlanView(TransactionMixin, APIView):

    def get(self, request, *args, **kwargs):

        query_params = PlanViewHelper.get_event_plan_params(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if 'error_message' in query_params:
            return JsonResponse(
                {'success': False, 'error_message': query_params['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        plan_manager = PlanImpl()
        response_data = plan_manager.fetch_event_plan(filters=query_params, user_id=member_id)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            {'success': True, 'event_plans': response_data['event_plans']},
            status=status_codes.HTTP_200_OK
        )


class UpdateEventPlanView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateEventPlanView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        validated_request = PlanViewHelper.validate_request_body_for_update_event_plan_view(request_body)

        if validated_request.get('error_message'):
            return JsonResponse(validated_request, status=status_codes.HTTP_400_BAD_REQUEST)

        plan_manager = PlanImpl()

        try:
            response_data = plan_manager.update_event_plan(request_body, member_id)

        except Exception as e:

            return JsonResponse({'error_message': e.args}, status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(response_data)


class FetchSamplePlanCategoryView(TransactionMixin, APIView):

    def get(self, request, *args, **kwargs):
        plan_manager = PlanImpl()

        response_data = plan_manager.fetch_sample_plan_category()

        if response_data.get('error_message'):
            context = ResponseUtilities.get_view_impl_error_context(response_data.get('error_message'),
                                                                    response_data.get('status'))
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse(response_data)


class FetchSamplePlanView(TransactionMixin, APIView):

    def get(self, request, *args, **kwargs):

        category_id = request.GET.get('category_id')

        if not category_id:
            return JsonResponse(**ResponseUtilities.get_view_impl_error_context('Invalid category_id',
                                                                                status_codes.HTTP_400_BAD_REQUEST))

        plan_manager = PlanImpl()

        response_data = plan_manager.fetch_sample_plans(category_id=category_id)

        if response_data.get('error_message'):
            return JsonResponse(**ResponseUtilities.get_view_impl_error_context(response_data.get('error_message'),
                                                                                status_codes.HTTP_400_BAD_REQUEST))

        return JsonResponse(response_data)
