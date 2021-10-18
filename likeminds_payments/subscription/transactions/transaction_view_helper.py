from .constants import *
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.model_utilities import ModelUtilities
from .models import Transaction
from ..plans.models import SubscriptionPlan
from ..payment_page.models import PaymentPageMeta


class TransactionViewHelper:

    @staticmethod
    def create_transaction_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'event' not in request_body or request_body['event'] not in VALID_WEBHOOK_EVENTS:
            return {'error_message': 'invalid event recognized'}

        if 'payload' not in request_body or not request_body['payload']:
            return {'error_message': 'no payload detected'}

        if request_body['event'] == VALID_WEBHOOK_EVENTS[0]:
            if 'refund' not in request_body['payload'] or not request_body['payload']['refund']:
                return {'error_message': 'no refund object detected'}

        if 'payment' not in request_body['payload'] or not request_body['payload']['payment']:
            return {'error_message': 'no payment object detected'}

        if 'entity' not in request_body['payload']['payment'] or not request_body['payload']['payment']['entity']:
            return {'error_message': 'no entity object detected'}

        return request_body

    @staticmethod
    def get_transactions_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        body = {
            'community_id': None,
            'user_id': None,
            'page': 1,
            'payment_page_id': None
        }

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id in body'}

        body['community_id'] = request_body['community_id']

        if 'user_id' in request_body:
            body['user_id'] = request_body['user_id']

        if 'page' in request_body and isinstance(request_body['page'], int):
            body['page'] = NumberUtilities.get_integer_from_string(request_body['page'])

        if 'payment_page_id' in request_body and request_body.get('payment_page_id'):
            payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                                  {'payment_page_id': request_body.get('payment_page_id')})

            if not payment_page_filter:
                return {'error_message': 'Invalid payment_page_id'}

            body['payment_page_id'] = request_body.get('payment_page_id')

        return body

    @staticmethod
    def get_transactions_instance_authenticator(community_id, user_id):

        has_permission_check = CoreServiceUtilities.has_permission(community_id, user_id)

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message']}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community'}

        return {'success': True}

    @staticmethod
    def refund_transaction_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        if 'transaction_id' not in request_body or not request_body['transaction_id']:
            return {'error_message': 'send transaction_id'}

        return request_body

    @staticmethod
    def refund_transaction_instance_authenticator(transaction_id, user_id):

        transaction_instance = Transaction.get_transaction_with_id_or_None(transaction_id)

        if transaction_instance is None:
            return {'error_message': 'invalid transaction id'}

        plan_instance = SubscriptionPlan.get_plan_or_None(transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'malformed transaction'}

        has_permission_check = CoreServiceUtilities.has_permission(plan_instance.community_id, user_id)

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message']}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community'}

        return {'transaction_instance': transaction_instance}

    @staticmethod
    def validate_request_params_for_event_transaction_view(user_id, chatroom_id):

        if not user_id:
            return {'error_message': "In-valid user id"}

        if not chatroom_id:
            return {'error_message': "In-valid chatroom id"}

        return {}

    @staticmethod
    def validate_request_params_for_event_payment_view(user_id, payment_id):

        if not user_id:
            return {'error_message': "In-valid user id"}

        if not payment_id:
            return {'error_message': "In-valid payment id"}

        return {}

    @staticmethod
    def validate_request_body_for_update_payment_view(req_body):

        if not req_body:
            return {'error_message': "In-valid request body"}

        if not req_body.get('payment_id'):
            return {'error_message': "In-valid payment id"}

        return {}

    @staticmethod
    def validate_request_body_for_download_all_transaction_view(req_body):

        if not req_body:
            return {'error_message': "Invalid request body"}

        if not req_body.get('payment_page_id'):
            return {'error_message': "Invalid payment_page_id"}

        return req_body
