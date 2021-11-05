from ..payment_page.constants import *
from .models import PaymentPageMeta
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.model_utilities import ModelUtilities


class PaymentPageViewHelper:

    @staticmethod
    def create_payment_page_body_validator(payment_page_meta_body, user_id):

        if not payment_page_meta_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        if 'community_id' not in payment_page_meta_body or not payment_page_meta_body['community_id']:
            return {'error_message': 'send community_id'}

        if 'title' not in payment_page_meta_body or not payment_page_meta_body['title']:
            return {'error_message': 'send title'}

        if 'amount_type' not in payment_page_meta_body or not payment_page_meta_body['amount_type']:
            return {'error_message': 'send amount_type'}

        if payment_page_meta_body['amount_type'] not in PAYMENT_PAGE_AMOUNT_TYPE_CHOICES:
            return {'error_message': 'invalid amount_type'}

        # if 'amount' not in payment_page_meta_body or not payment_page_meta_body['amount']:
        #     return {'error_message': 'send amount'}
        #
        # if not isinstance(payment_page_meta_body['amount'], int) or int(payment_page_meta_body['amount']) < 0:
        #     return {'error_message': 'invalid amount value'}

        if 'is_active' not in payment_page_meta_body or not payment_page_meta_body['is_active']:
            return {'error_message': 'send is_active'}

        return payment_page_meta_body

    @staticmethod
    def update_payment_page_body_validator(payment_page_meta_body, user_id):

        if 'payment_page_id' not in payment_page_meta_body:
            return {'error_message': 'send payment_page_id'}

        if 'community_id' in payment_page_meta_body:
            return {'error_message': 'community_id cannot be updated'}

        if 'amount' in payment_page_meta_body and not isinstance(payment_page_meta_body['amount'], (int, float)):
            return {'error_message': 'send amount as integer or decimal'}

        if 'amount_type' in payment_page_meta_body and \
                payment_page_meta_body['amount_type'] not in PAYMENT_PAGE_AMOUNT_TYPE_CHOICES:
            return {'error_message': 'invalid amount_type'}

        if 'contact_email' in payment_page_meta_body:
            return {'error_message': 'contact_email cannot be updated'}

        if 'contact_mobile_no' in payment_page_meta_body:
            return {'error_message': 'contact_mobile_no cannot be updated'}

        if 'contact_country_code' in payment_page_meta_body:
            return {'error_message': 'contact_country_code cannot be updated'}

        return payment_page_meta_body

    @staticmethod
    def fetch_all_payment_page_body_validator(payment_page_meta_body):

        if 'page' not in payment_page_meta_body:
            return {'error_message': 'send page'}

        if ('page' in payment_page_meta_body) and not payment_page_meta_body['page'].isdigit():
            return {'error_message': 'invalid page value'}

        if 'community_id' not in payment_page_meta_body:
            return {'error_message': 'send community_id'}

        if ('sort_type' in payment_page_meta_body) and (payment_page_meta_body['sort_type'] not in
                                                        [f.name for f in PaymentPageMeta._meta.get_fields()]):
            return {'error_message': 'invalid sort_type'}

        if ('sort_order' in payment_page_meta_body) and (str(payment_page_meta_body['sort_order']) not in
                                                         PAYMENT_PAGE_SORT_ORDER_CHOICES):
            return {'error_message': 'invalid sort_order'}

        return payment_page_meta_body

    @staticmethod
    def get_first_verified_email_and_phone(user_id, user_details_object=None):

        email = None
        mobile_no = None
        country_code = None

        if not user_details_object:
            user_details_object = CoreServiceUtilities.get_user_details({"member_id": user_id})

        if 'user' in user_details_object:

            if 'emails' not in user_details_object['user']:
                return {'error_message': 'error while fetching email'}

            else:

                for user_email_object in user_details_object['user']['emails']:

                    if user_email_object['verified']:
                        email = user_email_object['email']
                        break

            if 'mobiles' not in user_details_object['user']:
                return {'error_message': 'error while fetching mobile no'}

            else:

                for user_mobile_object in user_details_object['user']['mobiles']:

                    if user_mobile_object['state'] == 1:
                        mobile_no = user_mobile_object['mobile_no']
                        country_code = user_mobile_object['country_code']
                        break

        else:
            return {'error_message': 'error while fetching user details'}

        return {'email': email, 'mobile_no': mobile_no, 'country_code': country_code}

    @staticmethod
    def _create_new_payment_page_instance(payment_page_body, user_id) -> dict:

        if 'amount' in payment_page_body:
            payment_page_body['amount'] = NumberUtilities.convert_to_paisa_or_none(payment_page_body['amount'])

        else:
            payment_page_body['amount'] = 0

        if 'title' not in payment_page_body or not payment_page_body['title']:
            payment_page_body['title'] = ""

        if 'description' not in payment_page_body or not payment_page_body['description']:
            payment_page_body['description'] = ""

        if 'custom_success_message' not in payment_page_body or not payment_page_body['custom_success_message']:
            payment_page_body['custom_success_message'] = None

        if 'redirect_url' not in payment_page_body or not payment_page_body['redirect_url']:
            payment_page_body['redirect_url'] = None

        user_email_phone_object = PaymentPageViewHelper.get_first_verified_email_and_phone(user_id)

        if 'error_message' in user_email_phone_object:
            return {'error_message': user_email_phone_object['error_message']}

        if user_email_phone_object['email']:
            payment_page_body['contact_email'] = user_email_phone_object['email']

        else:
            payment_page_body['contact_email'] = None

        if user_email_phone_object['mobile_no']:
            payment_page_body['contact_mobile_no'] = user_email_phone_object['mobile_no']
            payment_page_body['contact_country_code'] = user_email_phone_object['country_code']

        else:
            payment_page_body['contact_mobile_no'] = None
            payment_page_body['contact_country_code'] = None

        payment_page_body['payment_page_url'] = None

        try:
            payment_page_instance = PaymentPageMeta.create_instance(payment_page_body)

        except Exception as error:
            print(error)
            return {'error_message': 'error while creating new plan'}

        payment_page_branch_url = CoreServiceUtilities.get_payment_page_url(payment_page_instance.community_id,
                                                                            payment_page_instance.payment_page_id)

        if 'payment_page_link' in payment_page_branch_url:
            payment_page_instance.payment_page_url = payment_page_branch_url['payment_page_link']
            payment_page_instance.save()

        return {'payment_page_instance': payment_page_instance}

    @staticmethod
    def _update_existing_page_instance(payment_page_body, payment_page_instance) -> dict:

        if 'title' in payment_page_body and payment_page_instance.title != payment_page_body['title']:
            payment_page_instance.title = payment_page_body['title']

        if 'description' in payment_page_body and payment_page_instance.description != payment_page_body['description']:
            payment_page_instance.description = payment_page_body['description']

        if 'amount_type' in payment_page_body and payment_page_instance.amount_type != payment_page_body['amount_type']\
                and payment_page_body['amount_type'] in PAYMENT_PAGE_AMOUNT_TYPE_CHOICES:
            payment_page_instance.amount_type = payment_page_body['amount_type']

        if 'amount' in payment_page_body:
            payment_page_instance.amount = NumberUtilities.convert_to_paisa_or_none(payment_page_body['amount'])

        if 'custom_success_message' in payment_page_body and \
                payment_page_instance.custom_success_message != payment_page_body['custom_success_message']:
            payment_page_instance.custom_success_message = payment_page_body['custom_success_message']

        if 'redirect_url' in payment_page_body and \
                payment_page_instance.redirect_url != payment_page_body['redirect_url']:
            payment_page_instance.redirect_url = payment_page_body['redirect_url']

        if 'is_active' in payment_page_body and payment_page_instance.is_active != payment_page_body['is_active']:
            payment_page_instance.is_active = payment_page_body['is_active']

        try:
            payment_page_instance.save()

        except:
            return {'error_message': 'error while updating existing plan'}

        return {'payment_page_instance': payment_page_instance}

    @staticmethod
    def check_cm_permission(community_id, user_id):

        has_permission_check = CoreServiceUtilities.has_permission(community_id, user_id)

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message']}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community'}

        return has_permission_check

    @staticmethod
    def create_payment_page_instance_helper(payment_page_body, user_id) -> dict:

        has_permission_check = PaymentPageViewHelper.check_cm_permission(payment_page_body['community_id'], user_id)

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message']}

        payment_page_instance = PaymentPageViewHelper._create_new_payment_page_instance(payment_page_body, user_id)

        if 'error_message' in payment_page_instance:
            return {'error_message': payment_page_instance['error_message']}

        return payment_page_instance

    @staticmethod
    def update_payment_page_instance_helper(payment_page_body, user_id) -> dict:

        if 'payment_page_id' not in payment_page_body:
            return {'error_message': 'send payment_page_id'}

        payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                              {"payment_page_id": payment_page_body['payment_page_id']})

        if not payment_page_filter:
            return {'error_message': 'invalid payment_page_id'}

        payment_page_instance = payment_page_filter[0]

        has_permission_check = PaymentPageViewHelper.check_cm_permission(payment_page_instance.community_id, user_id)

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message']}

        updated_plan_instance = PaymentPageViewHelper._update_existing_page_instance(payment_page_body,
                                                                                     payment_page_instance)

        if 'error_message' in updated_plan_instance:
            return {'error_message': updated_plan_instance['error_message']}

        return updated_plan_instance
