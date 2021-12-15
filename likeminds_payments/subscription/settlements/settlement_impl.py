from subscription.settlements.settlement_manager import SettlementManager
from subscription.settlements.serializers import SettlementSerializer
from rest_framework import status as status_codes
from subscription.utility.states import KYCState
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.time_utilities import TimeUtilities
from subscription.utility.request_utilities import RequestUtilities
from subscription.utility.response_utilities import ResponseUtilities
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.external_services.razorpay.razorpayX_wrapper import RazorpayXWrapper
from subscription.transactions.transaction_impl import TransactionImpl
from subscription.transactions.constants import (PAYMENTS_STATUS_FILTER)
from subscription.settlements.models import Settlement
from subscription.utility.states import SettlementStatus, TransactionType, TransactionRefundState
from subscription.kyc.models import CommunityKYC
from subscription.transactions.models import Transaction
from subscription.plans.models import SubscriptionEventPlan
from subscription.settlements.constants import (PAYOUT_MODE, PAYOUT_PURPOSE, PAYOUT_NARRATION, PAYOUT_QUEUE,
                                                PAYOUT_STATUS_MAP, SETTLEMENTS_PAGE_SIZE)
from subscription.utility.async_tasks import (settlement_processed_communication,
                                              settlement_failed_cm_communication,
                                              settlement_failed_admin_communication)
from django.conf import settings
import hmac
import hashlib
import json


class SettlementImpl(SettlementManager):

    community_id = None
    member_id = None
    x_username = None
    x_password = None

    def __init__(self, member_id: str = None, community_id: str = None, x_username: str = None, x_password: str = None):
        self.member_id = member_id
        self.community_id = community_id
        self.x_username = x_username
        self.x_password = x_password

    def get_member_id(self) -> str:
        return self.member_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_username(self) -> str:
        return self.x_username

    def get_password(self) -> str:
        return self.x_password

    def initiate_settlement(self) -> dict:

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

        settlement_instances = ModelUtilities.get_model_filter(
            Settlement, {'community_id': self.get_community_id()}).order_by('-created_at')

        kyc_instances = ModelUtilities.get_model_filter(CommunityKYC, {'community_id': self.get_community_id()})

        if len(kyc_instances) == 0:
            return ResponseUtilities.get_impl_error_context('No Kyc done for this community',
                                                            status_codes.HTTP_404_NOT_FOUND)

        kyc_instance = kyc_instances[0]

        if kyc_instance.status != KYCState.APPROVED or not kyc_instance.account_id:
            return ResponseUtilities.get_impl_error_context('KYC not approved yet', status_codes.HTTP_400_BAD_REQUEST)

        settlement_data = TransactionImpl.get_settlement_amount_data(self.get_community_id())

        if 'error_message' in settlement_data:
            return ResponseUtilities.get_impl_error_context(settlement_data.get('error_message'),
                                                            settlement_data.get('status'))

        if settlement_data.get('paid_amount', 0) == 0:
            return ResponseUtilities.get_impl_error_context('Not enough balance to settle',
                                                            status_codes.HTTP_400_BAD_REQUEST)

        current_time = TimeUtilities.current_time_in_milliseconds()

        payout_details = {
            'account_number': settings.RAZORPAY_X_ACCOUNT_NUMBER,
            'fund_account_id': kyc_instance.account_id,
            'amount': settlement_data.get('paid_amount'),
            'currency': kyc_instance.currency,
            'mode': PAYOUT_MODE,
            'purpose': PAYOUT_PURPOSE,
            'queue_if_low_balance': PAYOUT_QUEUE,
            'reference_id': '{}{}{}'.format(self.get_community_id(), current_time, settlement_data.get('paid_amount')),
            'narration': PAYOUT_NARRATION,
            'notes': {
                'start_epoch': settlement_data.get('start_epoch'),
                'end_epoch': current_time,
                'community_id': self.get_community_id()
            }
        }

        if len(settlement_instances) > 0:

            if settlement_instances[0].status in [SettlementStatus.QUEUED, SettlementStatus.INITIATED]:
                return ResponseUtilities.get_impl_error_context(
                    'Cannot initiate settlement, previous settlement in progress',
                    status_codes.HTTP_400_BAD_REQUEST)

            last_processed_settlement = settlement_instances.filter(status=SettlementStatus.PROCESSED).first()

            if last_processed_settlement:
                payout_details['notes']['start_epoch'] = last_processed_settlement.created_at

        razorpay_X_manager = RazorpayXWrapper()
        response = razorpay_X_manager.create_payout(payout_details)

        if 'error_message' in response:
            return ResponseUtilities.get_impl_error_context(
                'Payout initiation failed due to {}'.format(response['error_message']),
                status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

        return {'success': True}

    @staticmethod
    def _verify_payout_signature(payload, signature: str) -> dict:

        message = str(payload, 'utf-8')

        digest = hmac.new(
            key=bytes(settings.RAZORPAY_X_WEBHOOK_SECRET, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if digest != signature:
            return {'error_message': 'Signature mismatch'}

        return {'success': True}

    @staticmethod
    def _create_settlement_instance(settlement_body) -> dict:

        settlement_data = {
            'settlement_id': settlement_body.get('id'),
            'community_id': settlement_body['notes'].get('community_id'),
            'start_epoch': settlement_body['notes'].get('start_epoch'),
            'end_epoch': settlement_body['notes'].get('end_epoch'),
            'amount': settlement_body.get('amount'),
            'currency': settlement_body.get('currency'),
            'status': PAYOUT_STATUS_MAP[settlement_body.get('status')]
        }

        settlement_instance = SettlementSerializer(data=settlement_data)

        if settlement_instance.is_valid():
            settlement_instance.save()

            return {'settlement_instance': settlement_instance.data}

        return ResponseUtilities.get_impl_error_context(json.dumps(settlement_instance.errors),
                                                        status_codes.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _update_settlement_transactions(settlement_instance) -> dict:

        valid_event_plans = ModelUtilities.get_model_filter(SubscriptionEventPlan,
                                                            {'community_id': settlement_instance.community_id})

        valid_event_plan_ids = [plan.event_plan_id for plan in valid_event_plans]

        transaction_instances = (
            ModelUtilities.get_model_filter(Transaction, {'type_id': settlement_instance.community_id,
                                                          'type__in': [TransactionType.PAYMENT_PAGE,
                                                                       TransactionType.COMMUNITY_SUBSCRIPTION],
                                                          'created_at__gte': settlement_instance.start_epoch,
                                                          'created_at__lt': settlement_instance.end_epoch}) |
            ModelUtilities.get_model_filter(Transaction, {'plan_id__in': valid_event_plan_ids,
                                                          'type': TransactionType.EVENT,
                                                          'created_at__gte': settlement_instance.start_epoch,
                                                          'created_at__lt': settlement_instance.end_epoch
                                                          })
        )

        for transaction in transaction_instances:
            transaction.settlement_id = settlement_instance.settlement_id
            transaction.save()

        refund_transaction_instances = (
                ModelUtilities.get_model_filter(Transaction, {'type_id': settlement_instance.community_id,
                                                              'type__in': [TransactionType.PAYMENT_PAGE,
                                                                           TransactionType.COMMUNITY_SUBSCRIPTION],
                                                              'status': PAYMENTS_STATUS_FILTER['REFUNDED'],
                                                              'refund_handled': TransactionRefundState.NOT_HANDLED}) |
                ModelUtilities.get_model_filter(Transaction, {'plan_id__in': valid_event_plan_ids,
                                                              'type': TransactionType.EVENT,
                                                              'status': PAYMENTS_STATUS_FILTER['REFUNDED'],
                                                              'refund_handled': TransactionRefundState.NOT_HANDLED
                                                              })
        )

        for transaction in refund_transaction_instances:
            transaction.refund_handled = TransactionRefundState.HANDLED
            transaction.save()

        return {'success': True}

    def create_settlement(self, settlement_data) -> dict:

        payout_raw_body = settlement_data.get('payout_raw_body')
        payout_signature = settlement_data.get('payout_signature')
        payout_body = settlement_data.get('payout_body')
        payout_entity = payout_body['payload']['payout']['entity']

        signature_verification = self._verify_payout_signature(payout_raw_body, payout_signature)

        if 'error_message' in signature_verification:
            return {'error_message': signature_verification['error_message']}

        existing_settlement_list = ModelUtilities.get_model_filter(
            Settlement, {'settlement_id': payout_entity.get('id')})

        if len(existing_settlement_list) > 0:
            settlement_instance = existing_settlement_list[0]
            settlement_instance.status = PAYOUT_STATUS_MAP[payout_entity.get('status')]
            settlement_instance.save()

        else:
            create_settlement = self._create_settlement_instance(payout_entity)

            if 'error_message' in create_settlement:
                return ResponseUtilities(create_settlement['error_message'], create_settlement['status'])

            settlement_instance = create_settlement['settlement_instance']

        if PAYOUT_STATUS_MAP[payout_entity.get('status')] == SettlementStatus.PROCESSED:
            self._update_settlement_transactions(settlement_instance)

            # email communication for processed settlement
            settlement_processed_communication.delay(settlement_instance.id)

        if PAYOUT_STATUS_MAP[payout_entity.get('status')] in [SettlementStatus.FAILED, SettlementStatus.REVERSED]:

            # email communication for failed settlement
            settlement_failed_cm_communication.delay(settlement_instance.id)
            settlement_failed_admin_communication.delay(settlement_instance.id)

        return {'success': True}

    def fetch_settlement(self, filters=None, page=None) -> dict:

        if not self.get_member_id():

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

        settlements = ModelUtilities.get_model_filter(Settlement, filters).order_by('-created_at')

        if len(settlements) == 0:
            return ResponseUtilities.get_impl_error_context('No settlement found for given details',
                                                            status_codes.HTTP_404_NOT_FOUND)

        paginated_settlements = ModelUtilities.paginate_queryset(settlements, page, SETTLEMENTS_PAGE_SIZE)

        return {'settlements': SettlementSerializer(paginated_settlements, many=True).data}
