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

        if not user_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send member_id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

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
            {'success': True, 'payment_page_id': instance_data['payment_page_instance'].payment_page_id},
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

        if not user_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send member_id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

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


class FetchAllPaymentPageView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        user_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if not user_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send member_id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        query_params = RequestUtilities.fetch_request_query_params(request)

        validated_request_body = PaymentPageViewHelper.fetch_all_payment_page_body_validator(query_params)

        if 'error_message' in validated_request_body:
            return JsonResponse(
                {'success': False, 'error_message': validated_request_body['error_message']},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        payment_page_manager = PaymentPageImpl(user_id=user_id, community_id=validated_request_body['community_id'])
        response_data = payment_page_manager.fetch_all_payment_page(validated_request_body)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            response_data,
            status=status_codes.HTTP_200_OK
        )


class FetchPaymentPageView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if not member_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send member_id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        payment_page_id = request.GET.get('payment_page_id', None)

        if not payment_page_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send payment_page_id'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        payment_page_manager = PaymentPageImpl(user_id=member_id)
        response_data = payment_page_manager.fetch_payment_page(payment_page_id)

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            response_data,
            status=status_codes.HTTP_200_OK
        )


class FetchContactUsView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if not member_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send member_id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        payment_page_manager = PaymentPageImpl(user_id=member_id)
        response_data = payment_page_manager.fetch_contact_us()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            response_data,
            status=status_codes.HTTP_200_OK
        )


class DownloadAllPaymentPageView(APIView):

    @staticmethod
    def get(request, *args, **kwargs):

        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        if not member_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send member_id in headers'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        community_id = request.GET.get('community_id', None)

        if not community_id:
            return JsonResponse(
                {'success': False, 'error_message': 'send community_id'},
                status=status_codes.HTTP_400_BAD_REQUEST
            )

        payment_page_manager = PaymentPageImpl(user_id=member_id, community_id=community_id)
        response_data = payment_page_manager.download_all_payment_page()

        if 'error_message' in response_data:
            return JsonResponse(
                {'success': False, 'error_message': response_data['error_message']},
                status=status_codes.HTTP_200_OK
            )

        return JsonResponse(
            response_data,
            status=status_codes.HTTP_200_OK
        )
