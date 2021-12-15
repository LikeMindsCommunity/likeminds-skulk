from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from ..utility.response_utilities import ResponseUtilities
from ..utility.number_utilities import NumberUtilities
from .settlement_impl import SettlementImpl
from .settlement_view_helper import SettlementViewHelper


class InitiateSettlementView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(InitiateSettlementView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        validated_request_body = SettlementViewHelper.initiate_settlement_body_validator(request_body, member_id)

        if 'error_message' in validated_request_body:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_body['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        settlement_manager = SettlementImpl(community_id=validated_request_body.get('community_id'),
                                            member_id=member_id)
        response_data = settlement_manager.initiate_settlement()

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class CreateSettlementView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateSettlementView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        validated_request_body = SettlementViewHelper.create_settlement_body_validator(request_body)
        razorpay_signature = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_RAZORPAY_SIGNATURE')

        raw_body = request.body

        if not razorpay_signature or 'error_message' in validated_request_body:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_body['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        settlement_manager = SettlementImpl()
        response_data = settlement_manager.create_settlement({'payout_raw_body': raw_body,
                                                              'payout_signature': razorpay_signature,
                                                              'payout_body': validated_request_body})

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse(
            {'success': True},
            status=status_codes.HTTP_200_OK
        )


class FetchSettlementView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FetchSettlementView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):

        query_params = SettlementViewHelper.get_settlements_query_params(request)
        x_username = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_USERNAME')
        x_password = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_PASSWORD')
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        page = NumberUtilities.get_integer_from_string(request.GET.get('page', 1))

        if 'error_message' in query_params:
            context = ResponseUtilities.get_view_impl_error_context(query_params['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        settlement_manager = SettlementImpl(community_id=query_params['community_id'], member_id=member_id,
                                            x_username=x_username, x_password=x_password)
        response_data = settlement_manager.fetch_settlement(query_params, page)

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse(
            {'success': True, 'settlements': response_data['settlements']},
            status=status_codes.HTTP_200_OK
        )
