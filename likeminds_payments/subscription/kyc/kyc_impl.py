import json
from subscription.kyc.kyc_manager import KYCManager
from subscription.kyc.constants import KYC_LIST_PAGE_SIZE
from subscription.kyc.serializers import KycSerializer
from rest_framework import status as status_codes
from subscription.utility.states import KYCState
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.number_utilities import NumberUtilities
from subscription.utility.string_utilities import StringUtilities
from subscription.utility.request_utilities import RequestUtilities
from subscription.utility.response_utilities import ResponseUtilities
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.external_services.razorpay.razorpayX_wrapper import RazorpayXWrapper
from subscription.kyc.models import CommunityKYC


class KycImpl(KYCManager):

    member_id = None
    community_id = None
    username = None
    password = None

    def __init__(self, member_id: str = None, community_id: str = None, username: str = None, password: str = None):
        self.member_id = member_id
        self.community_id = community_id
        self.username = username
        self.password = password

    def get_member_id(self) -> str:
        return self.member_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password

    def add_kyc(self, request_body) -> dict:

        if not self.get_member_id() or not self.get_community_id():
            return ResponseUtilities.get_impl_error_context('send x-member-id in headers and community_id in body',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

        if 'error_message' in has_permission_check:
            return ResponseUtilities.get_impl_error_context(has_permission_check['error_message'],
                                                            status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return ResponseUtilities.get_impl_error_context('You are not the Owner/CM of the community',
                                                            status_codes.HTTP_401_UNAUTHORIZED)

        if ModelUtilities.is_model_filter_exists(CommunityKYC, {'community_id': self.get_community_id()}):
            return ResponseUtilities.get_impl_error_context('KYC record already exists!',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        request_body['user_id'] = NumberUtilities.get_integer_from_string(self.get_member_id())
        kyc_serializer = KycSerializer(data=request_body)

        if kyc_serializer.is_valid():
            kyc_serializer.save()
            return {'kyc': kyc_serializer.data, 'status': status_codes.HTTP_201_CREATED}

        return ResponseUtilities.get_impl_error_context(json.dumps(kyc_serializer.errors),
                                                        status_codes.HTTP_400_BAD_REQUEST)

    def upload_kyc(self, request_body) -> dict:

        if self.get_member_id() is None or self.get_community_id() is None:
            return ResponseUtilities.get_impl_error_context('send x-member-id in headers and community_id in body',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

        if 'error_message' in has_permission_check:
            return ResponseUtilities.get_impl_error_context(has_permission_check['error_message'],
                                                            status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return ResponseUtilities.get_impl_error_context('You are not the Owner/CM of the community',
                                                            status_codes.HTTP_401_UNAUTHORIZED)

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instances) == 0:
            return ResponseUtilities.get_impl_error_context('No KYC instance found for this community',
                                                            status_codes.HTTP_404_NOT_FOUND)

        kyc_instance = kyc_instances[0]

        if kyc_instance.doc_front_url is not None and request_body['doc_front_url'] is not None:
            return ResponseUtilities.get_impl_error_context('KYC doc already uploaded for doc_front_url!',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        if kyc_instance.doc_back_url is not None and request_body['doc_back_url'] is not None:
            return ResponseUtilities.get_impl_error_context('KYC doc already uploaded for doc_back_url!',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        if kyc_instance.doc_pan_url is not None and request_body['doc_pan_url'] is not None:
            return ResponseUtilities.get_impl_error_context('KYC doc already uploaded for doc_pan_url!',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        if request_body['doc_front_url'] is not None:
            kyc_instance.doc_front_url = request_body.get('doc_front_url')

        if request_body['doc_back_url'] is not None:
            kyc_instance.doc_back_url = request_body.get('doc_back_url')

        if request_body['doc_pan_url'] is not None:
            kyc_instance.doc_pan_url = request_body.get('doc_pan_url')

        kyc_instance.save()

        return {'kyc': KycSerializer(kyc_instance).data, 'status': status_codes.HTTP_200_OK}

    def fetch_kyc(self) -> dict:

        if self.get_member_id() is None:

            if self.get_username() is None or self.get_password() is None:
                return ResponseUtilities.get_impl_error_context('send x-member-id or x-username/x-password in headers',
                                                                status_codes.HTTP_400_BAD_REQUEST)

            if not RequestUtilities.verify_growth_authentication(self.get_username(), self.get_password()):
                return ResponseUtilities.get_impl_error_context('You are not authorized to perform this operation',
                                                                status_codes.HTTP_401_UNAUTHORIZED)

        else:
            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return ResponseUtilities.get_impl_error_context(has_permission_check['error_message'],
                                                                status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            if 'has_permission' in has_permission_check and not has_permission_check['has_permission']:
                return ResponseUtilities.get_impl_error_context('You are not the Owner/CM of the community',
                                                                status_codes.HTTP_401_UNAUTHORIZED)

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instances) == 0:
            return ResponseUtilities.get_impl_error_context('No kyc record found for given community_id',
                                                            status_codes.HTTP_404_NOT_FOUND)

        return {'kyc': KycSerializer(kyc_instances[0]).data, 'status': status_codes.HTTP_200_OK}

    def fetch_all_kyc(self, page: int = 1) -> dict:

        if self.get_username() is None or self.get_password() is None:
            return ResponseUtilities.get_impl_error_context('x-username/x-password in headers',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        if not RequestUtilities.verify_growth_authentication(self.get_username(), self.get_password()):
            return ResponseUtilities.get_impl_error_context('You are not authorized to perform this operation',
                                                            status_codes.HTTP_401_UNAUTHORIZED)

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {}).order_by('-created_at')
        output = ModelUtilities.paginate_queryset(kyc_instances, page, KYC_LIST_PAGE_SIZE)

        return {'kyc': KycSerializer(output, many=True).data, 'status': status_codes.HTTP_200_OK}

    def edit_kyc(self, request_body) -> dict:

        if self.get_username() is None or self.get_password() is None:
            return ResponseUtilities.get_impl_error_context('x-username/x-password in headers',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        if not RequestUtilities.verify_growth_authentication(self.get_username(), self.get_password()):
            return ResponseUtilities.get_impl_error_context('You are not authorized to perform this operation',
                                                            status_codes.HTTP_401_UNAUTHORIZED)

        kyc_instance = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instance) == 0:
            return ResponseUtilities.get_impl_error_context('No kyc instance for given community',
                                                            status_codes.HTTP_404_NOT_FOUND)

        serializer = KycSerializer()
        updated_kyc_instance = serializer.update(kyc_instance[0], request_body)

        if updated_kyc_instance.status == KYCState.APPROVED:

            # Create a contact if it doesn't exist
            if updated_kyc_instance.contact_id is None:
                user_details = CoreServiceUtilities.user_fetch({'member_id': updated_kyc_instance.user_id})

                if 'user' in user_details:
                    email = user_details['user']['emails'][0]
                    phone = user_details['user']['mobiles'][0]

                    contact_details = {
                        'name': updated_kyc_instance.name,
                        'user_id': StringUtilities.get_string_from_integer(updated_kyc_instance.user_id),
                        'email': email['email'],
                        'phone': '{}{}'.format(phone['country_code'], phone['mobile_no'])
                    }

                    razorpay_X_manager = RazorpayXWrapper()
                    response = razorpay_X_manager.create_contact(contact_details)

                    if 'error_message' in response:
                        return ResponseUtilities.get_impl_error_context(
                            'KYC updated but status activation failed due to {}'.format(response['error_message']),
                            status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

                    if 'contact' in response:
                        updated_kyc_instance.contact_id = response['contact'].get('id', None)
                        updated_kyc_instance.save()

                # case if the user details fails
                else:
                    updated_kyc_instance.status = KYCState.PENDING_APPROVAL
                    updated_kyc_instance.save()

            # Create a fund account if it doesn't exist
            if updated_kyc_instance.account_id is None and updated_kyc_instance.contact_id is not None:
                account_details = {
                    'contact_id': updated_kyc_instance.contact_id,
                    'account_type': 'bank_account',
                    'bank_account': {
                        'name': updated_kyc_instance.bank_user_name,
                        'ifsc': updated_kyc_instance.bank_ifsc_code,
                        'account_number': updated_kyc_instance.account_number
                    }
                }

                razorpay_X_manager = RazorpayXWrapper()
                response = razorpay_X_manager.create_fund_account(account_details)

                if 'error_message' in response:
                    return ResponseUtilities.get_impl_error_context(
                        'KYC updated but status activation failed due to {}'.format(response['error_message']),
                        status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

                if 'account' in response:
                    updated_kyc_instance.account_id = response['account'].get('id', None)
                    updated_kyc_instance.save()

        return {'kyc': KycSerializer(updated_kyc_instance).data, 'status': status_codes.HTTP_200_OK}
