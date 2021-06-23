from .constants import *
from ..utility.core_service_utilities import CoreServiceUtilities
from .models import Transaction
from ..plans.models import SubscriptionPlan


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

        if 'user_id' not in request_body or not request_body['user_id']:
            return {'error_message': 'send user_id in body'}

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id in body'}

        return request_body

    @staticmethod
    def get_transactions_instance_authenticator(community_id, user_id):

        is_owner_check = CoreServiceUtilities.is_owner(community_id, user_id)

        if 'error_message' in is_owner_check:
            return {'error_message': is_owner_check['error_message']}

        if 'is_owner' in is_owner_check and is_owner_check['is_owner'] is False:
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

        is_owner_check = CoreServiceUtilities.is_owner(plan_instance.community_id, user_id)

        if 'error_message' in is_owner_check:
            return {'error_message': is_owner_check['error_message']}

        if 'is_owner' in is_owner_check and is_owner_check['is_owner'] is False:
            return {'error_message': 'You are not the Owner/CM of the community'}

        return {'transaction_instance': transaction_instance}
