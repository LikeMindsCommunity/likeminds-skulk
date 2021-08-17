from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from ..orders.order_view_helper import OrderViewHelper
from .lead_impl import LeadImpl
from .lead_view_helper import LeadViewHelper


class SendEventView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SendEventView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)

        validated_request_body = LeadViewHelper.send_facebook_event_body_validator(request_body)

        client_ip_address = OrderViewHelper.get_ip(request)
        event_source_url = RequestUtilities.get_parameter_from_headers(request, 'HTTP_REFERER')
        client_user_agent = RequestUtilities.get_parameter_from_headers(request, 'HTTP_USER_AGENT')

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        lead_manager = LeadImpl()
        response_data = lead_manager.send_facebook_event(
            client_ip_address, client_user_agent, validated_request_body['event_name'],
            validated_request_body['action_source'], validated_request_body['emails'], validated_request_body['phones'],
            validated_request_body['fbc'], validated_request_body['fbp'], event_source_url)

        return JsonResponse(
            response_data,
            status=status_codes.HTTP_200_OK
        )
