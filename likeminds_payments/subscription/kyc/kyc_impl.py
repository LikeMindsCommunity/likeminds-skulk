from .kyc_manager import KYCManager
from .constants import *
from .serializers import KycSerializer, MultipleKycSerializer
from rest_framework import status as status_codes
from ..utility.states import KYCState
from ..utility.model_utilities import ModelUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.string_utilities import StringUtilities
from ..utility.request_utilities import RequestUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from ..external_services.razorpay.razorpayX_wrapper import RazorpayXWrapper
from ..kyc.models import CommunityKYC


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

        if self.get_member_id() is None or self.get_community_id() is None:
            return {'error_message': 'send x-member-id in headers and community_id in body',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message'],
                    'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community',
                    'status': status_codes.HTTP_401_UNAUTHORIZED}

        if ModelUtilities.is_model_filter_exists(CommunityKYC, {'community_id': self.get_community_id()}):
            return {'error_message': 'KYC record already exists!', 'status': status_codes.HTTP_400_BAD_REQUEST}

        request_body['user_id'] = NumberUtilities.get_integer_from_string(self.get_member_id())
        kyc_instance = CommunityKYC.create_instance(request_body)

        return {'kyc': KycSerializer(kyc_instance), 'status': status_codes.HTTP_201_CREATED}

    def upload_kyc(self, request_body) -> dict:

        if self.get_member_id() is None or self.get_community_id() is None:
            return {'error_message': 'send x-member-id in headers and community_id in body',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message'],
                    'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community',
                    'status': status_codes.HTTP_401_UNAUTHORIZED}

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instances) == 0:
            return {'error_message': 'No KYC instance found for this community',
                    'status': status_codes.HTTP_404_NOT_FOUND}

        kyc_instance = kyc_instances[0]

        if kyc_instance.doc_front_url is not None and request_body['doc_front_url'] is not None:
            return {'error_message': 'KYC doc already uploaded for doc_front_url!',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        if kyc_instance.doc_back_url is not None and request_body['doc_back_url'] is not None:
            return {'error_message': 'KYC doc already uploaded for doc_back_url!',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        if kyc_instance.doc_pan_url is not None and request_body['doc_pan_url'] is not None:
            return {'error_message': 'KYC doc already uploaded for doc_pan_url!',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        if request_body['doc_front_url'] is not None:
            kyc_instance.doc_front_url = request_body.get('doc_front_url')

        if request_body['doc_back_url'] is not None:
            kyc_instance.doc_back_url = request_body.get('doc_back_url')

        if request_body['doc_pan_url'] is not None:
            kyc_instance.doc_pan_url = request_body.get('doc_pan_url')

        kyc_instance.save()

        return {'kyc': KycSerializer(kyc_instance), 'status': status_codes.HTTP_200_OK}

    def fetch_kyc(self) -> dict:

        if self.get_member_id() is None:

            if self.get_username() is None or self.get_password() is None:
                return {'error_message': 'send x-member-id or x-username/x-password in headers',
                        'status': status_codes.HTTP_400_BAD_REQUEST}

            if not RequestUtilities.verify_growth_authentication(self.get_username(), self.get_password()):
                return {'error_message': 'You are not authorized to perform this operation',
                        'status': status_codes.HTTP_401_UNAUTHORIZED}

        else:
            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message'],
                        'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community',
                        'status': status_codes.HTTP_401_UNAUTHORIZED}

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instances) == 0:
            return {'error_message': 'No kyc record found for given community_id',
                    'status': status_codes.HTTP_404_NOT_FOUND}

        return {'kyc': KycSerializer(kyc_instances[0]), 'status': status_codes.HTTP_200_OK}

    def fetch_all_kyc(self, page: int = 1) -> dict:

        if self.get_username() is None or self.get_password() is None:
            return {'error_message': 'x-username/x-password in headers',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        if not RequestUtilities.verify_growth_authentication(self.get_username(), self.get_password()):
            return {'error_message': 'You are not authorized to perform this operation',
                    'status': status_codes.HTTP_401_UNAUTHORIZED}

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {}).order_by('-created_at')
        output = ModelUtilities.paginate_queryset(kyc_instances, page, PAGE_SIZE)

        return {'kyc': MultipleKycSerializer(output), 'status': status_codes.HTTP_200_OK}

    @staticmethod
    def _update_kyc_instance(kyc_instance, kyc_data):
        kyc_instance.name = kyc_data.get('name', kyc_instance.name)
        kyc_instance.address = kyc_data.get('address', kyc_instance.address)
        kyc_instance.doc_type = kyc_data.get('doc_type', kyc_instance.doc_type)
        kyc_instance.doc_number = kyc_data.get('doc_number', kyc_instance.doc_number)
        kyc_instance.doc_front_url = kyc_data.get('doc_front_url', kyc_instance.doc_front_url)
        kyc_instance.doc_back_url = kyc_data.get('doc_back_url', kyc_instance.doc_back_url)
        kyc_instance.doc_pan_number = kyc_data.get('doc_pan_number', kyc_instance.doc_pan_number)
        kyc_instance.doc_pan_url = kyc_data.get('doc_pan_url', kyc_instance.doc_pan_url)
        kyc_instance.gstn = kyc_data.get('gstn', kyc_instance.gstn)
        kyc_instance.bank_user_name = kyc_data.get('bank_user_name', kyc_instance.bank_user_name)
        kyc_instance.bank_ifsc_code = kyc_data.get('bank_ifsc_code', kyc_instance.bank_ifsc_code)
        kyc_instance.account_number = kyc_data.get('account_number', kyc_instance.account_number)
        kyc_instance.bank_name = kyc_data.get('bank_name', kyc_instance.bank_name)
        kyc_instance.status = kyc_data.get('status', kyc_instance.status)

        kyc_instance.save()

        return kyc_instance

    def edit_kyc(self, request_body) -> dict:

        if self.get_username() is None or self.get_password() is None:
            return {'error_message': 'x-username/x-password in headers',
                    'status': status_codes.HTTP_400_BAD_REQUEST}

        if not RequestUtilities.verify_growth_authentication(self.get_username(), self.get_password()):
            return {'error_message': 'You are not authorized to perform this operation',
                    'status': status_codes.HTTP_401_UNAUTHORIZED}

        kyc_instance = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instance) == 0:
            return {'error_message': 'No kyc instance for given community', 'status': status_codes.HTTP_404_NOT_FOUND}

        updated_kyc_instance = self._update_kyc_instance(kyc_instance[0], request_body)

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

                if 'account' in response:
                    updated_kyc_instance.account_id = response['account'].get('id', None)
                    updated_kyc_instance.save()

        return {'kyc': KycSerializer(updated_kyc_instance), 'status': status_codes.HTTP_200_OK}
