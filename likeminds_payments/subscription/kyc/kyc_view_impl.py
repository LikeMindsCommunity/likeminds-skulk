from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status as status_codes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utility.request_utilities import RequestUtilities
from ..utility.response_utilities import ResponseUtilities
from .kyc_impl import KycImpl
from .kyc_view_helper import KycViewHelper


class CreateKycView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateKycView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = KycViewHelper.create_kyc_body_validator(request_body, member_id)

        if 'error_message' in validated_request_body:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_body['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        kyc_manager = KycImpl(member_id=member_id, community_id=validated_request_body['community_id'])
        response_data = kyc_manager.add_kyc(validated_request_body)

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse({'success': True, 'kyc': response_data['kyc']}, status=response_data['status'])


class UploadKycView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UploadKycView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')

        validated_request_body = KycViewHelper.upload_kyc_body_validator(request_body, member_id)

        if 'error_message' in validated_request_body:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_body['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        kyc_manager = KycImpl(member_id=member_id, community_id=validated_request_body['community_id'])
        response_data = kyc_manager.upload_kyc(validated_request_body)

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse({'success': True, 'kyc': response_data['kyc']}, status=response_data['status'])


class FetchKycView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FetchKycView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):

        request_params = RequestUtilities.fetch_request_query_params(request)
        member_id = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_MEMBER_ID')
        x_username = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_USERNAME')
        x_password = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_PASSWORD')

        validated_request_params = KycViewHelper.fetch_kyc_validator(request_params, member_id, x_username, x_password)

        if 'error_message' in validated_request_params:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_params['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        kyc_manager = KycImpl(member_id=validated_request_params['member_id'],
                              community_id=validated_request_params['community_id'],
                              username=validated_request_params['x_username'],
                              password=validated_request_params['x_password'])
        response_data = kyc_manager.fetch_kyc()

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse({'success': True,
                             'kyc': response_data['kyc'],
                             'show_kyc_banner': response_data['show_kyc_banner']},
                            status=response_data['status'])


class FetchAllKycView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FetchAllKycView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):

        request_params = RequestUtilities.fetch_request_query_params(request)
        x_username = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_USERNAME')
        x_password = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_PASSWORD')

        validated_request_params = KycViewHelper.fetch_all_kyc_validator(request_params, x_username, x_password)

        if 'error_message' in validated_request_params:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_params['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        kyc_manager = KycImpl(username=validated_request_params['x_username'],
                              password=validated_request_params['x_password'])
        response_data = kyc_manager.fetch_all_kyc(page=validated_request_params['page'])

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse({'success': True, 'kyc': response_data['kyc']}, status=response_data['status'])


class EditKycView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(EditKycView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):

        request_body = RequestUtilities.load_request_body(request)
        x_username = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_USERNAME')
        x_password = RequestUtilities.get_parameter_from_headers(request, 'HTTP_X_PASSWORD')

        validated_request_body = KycViewHelper.edit_kyc_body_validator(request_body, x_username, x_password)

        if 'error_message' in validated_request_body:
            context = ResponseUtilities.get_view_impl_error_context(validated_request_body['error_message'],
                                                                    status_codes.HTTP_400_BAD_REQUEST)
            return JsonResponse(context['data'], status=context['status'])

        kyc_manager = KycImpl(community_id=validated_request_body['community_id'],
                              username=x_username,
                              password=x_password)
        response_data = kyc_manager.edit_kyc(validated_request_body)

        if 'error_message' in response_data:
            context = ResponseUtilities.get_view_impl_error_context(response_data['error_message'],
                                                                    response_data['status'])
            return JsonResponse(context['data'], status=context['status'])

        return JsonResponse({'success': True, 'kyc': response_data['kyc']}, status=response_data['status'])
