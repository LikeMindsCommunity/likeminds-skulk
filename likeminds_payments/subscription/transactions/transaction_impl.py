from __future__ import absolute_import, unicode_literals

import uuid

import pandas as pd
from celery import shared_task
from .transaction_manager import TransactionManager
from django.conf import settings
from django.db.models import Sum, Count, Min
from django.template.loader import get_template
import time
from rest_framework import status as status_codes
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper
from ..external_services.segment.segment_impl import SegmentImpl
from ..utility.number_utilities import NumberUtilities
from ..utility.states import TransactionType, SettlementStatus, TransactionRefundState, MemberState, \
    TransactionStatusType
from ..utility.time_utilities import TimeUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from subscription.utility.response_utilities import ResponseUtilities
from ..utility.async_tasks import (payment_page_member_payment_success_email, payment_page_member_payment_failed_email,
                                   payment_page_cm_payment_success_email, send_email_from_core_service,
                                   payment_success_membership_join_communication)
from ..utility.csv_utilities import CsvUtilities
from .constants import *
from .models import Transaction
from subscription.settlements.models import Settlement
from ..plans.models import SubscriptionPlan, SubscriptionEventPlan
from ..subscriptions.models import Subscription
from ..payment_page.models import PaymentPageMeta
from ..payment_page.payment_page_view_helper import PaymentPageViewHelper
from ..subscription_histories.models import SubscriptionHistory
from subscription.plans.models import SubscriptionEventPlan
from subscription.subscriptions.constants import LIFETIME_VALID_TILL, MIGRATION, MANUAL_PAYMENT_PAGE, LIFETIME_PAYMENT
from ..member_acquisition.models import MemberAcquisition
from ..subscriptions.subscription_view_impl import SubscriptionImpl
from .serializers import TransactionSerializer

from ..external_services.s3.s3_wrapper import S3Wrapper

import hmac
import hashlib
import razorpay
import analytics


class TransactionImpl(TransactionManager):
    transaction_body = None
    transaction_raw_body = None
    transaction_signature = None
    user_id = None
    community_id = None
    transaction_instance = None

    def __init__(self, transaction_body: dict = None, transaction_raw_body: bytes = None,
                 transaction_signature: str = None, user_id: str = None, community_id: str = None,
                 transaction_instance: Transaction = None):
        self.transaction_body = transaction_body
        self.transaction_raw_body = transaction_raw_body
        self.transaction_signature = transaction_signature
        self.user_id = user_id
        self.community_id = community_id
        self.transaction_instance = transaction_instance

    def get_transaction_body(self) -> dict:
        return self.transaction_body

    def get_transaction_raw_body(self) -> bytes:
        return self.transaction_raw_body

    def get_transaction_signature(self) -> str:
        return self.transaction_signature

    def get_user_id(self) -> str:
        return self.user_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_transaction_instance(self) -> Transaction:
        return self.transaction_instance

    @staticmethod
    def _verify_transaction_signature(payload, signature: str) -> dict:

        message = str(payload, 'utf-8')

        digest = hmac.new(
            key=bytes(settings.RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if digest != signature:
            return {'error_message': 'Signature mismatch'}

        return {'success': True}

    @staticmethod
    def _fetch_transaction_data_for_community_subscription(order_notes, payment_instance, refund_instance):

        transaction_data = {
            "plan_id": order_notes.get('plan_id'),
            "payment_id": payment_instance['id'],
            "community_name": order_notes.get('community_name'),
            "plan_name": order_notes.get('name', ''),
            "plan_cost": payment_instance['amount'],
            "renew": False,
            "amount": payment_instance['amount'],
            "payment_email": payment_instance['email'],
            "payment_phone": payment_instance['contact'],
            "currency": payment_instance['currency'],
            "is_international": payment_instance['international'],
            "method": payment_instance['method'],
            "status": payment_instance['status'],
            "error_description": "",
            "refund_amount": 0,
            "user_id": None,
            "payment_page_url": order_notes.get('payment_page_url'),
            "shared_by": None,
            "grace_period": 0,
            "type": TransactionType.COMMUNITY_SUBSCRIPTION
        }

        if payment_instance['error_description'] is not None:
            transaction_data["error_description"] = payment_instance['error_description']

        if 'renew' in order_notes and order_notes['renew'] == "true":
            transaction_data['renew'] = True

        if 'amount' in refund_instance:
            transaction_data['refund_amount'] = refund_instance['amount']

        if 'user_id' in order_notes and transaction_data['renew']:
            transaction_data['user_id'] = order_notes['user_id']

        if 'shared_by' in order_notes:
            transaction_data['shared_by'] = order_notes['shared_by']

        if 'grace_period' in order_notes:
            transaction_data['grace_period'] = order_notes['grace_period']

        return transaction_data

    @staticmethod
    def _fetch_transaction_data_for_event(order_notes, payment_instance, refund_instance):

        transaction_data = {
            "plan_id": order_notes['event_plan_id'],
            "payment_id": payment_instance['id'],
            "community_name": order_notes['community_name'],
            "community_id": order_notes['community_id'],
            "plan_cost": payment_instance['amount'],
            "renew": False,
            "amount": payment_instance['amount'],
            "payment_email": payment_instance['email'],
            "payment_phone": payment_instance['contact'],
            "currency": payment_instance['currency'],
            "is_international": payment_instance['international'],
            "method": payment_instance['method'],
            "status": payment_instance['status'],
            "error_description": "",
            "refund_amount": 0,
            "user_id": order_notes.get('user_id'),
            "payment_page_url": order_notes['payment_page_url'],
            "grace_period": 0,
            "type": TransactionType.EVENT,
            "shared_by": None
        }

        if payment_instance['error_description'] is not None:
            transaction_data["error_description"] = payment_instance['error_description']

        if 'renew' in order_notes and order_notes['renew'] == "true":
            transaction_data['renew'] = True

        if 'amount' in refund_instance:
            transaction_data['refund_amount'] = refund_instance['amount']

        if 'user_id' in order_notes:
            transaction_data['user_id'] = order_notes['user_id']

        if 'shared_by' in order_notes:
            transaction_data['shared_by'] = order_notes['shared_by']

        if 'grace_period' in order_notes:
            transaction_data['grace_period'] = order_notes['grace_period']

        return transaction_data

    @staticmethod
    def _fetch_transaction_data_for_payment_page(order_notes, payment_instance, refund_instance):

        transaction_data = {
            "plan_id": order_notes['payment_page_id'],
            "payment_id": payment_instance['id'],
            "community_name": order_notes['community_name'],
            "type_id": order_notes['community_id'],
            "plan_cost": payment_instance['amount'],
            "amount": payment_instance['amount'],
            "renew": False,
            "payment_email": payment_instance['email'],
            "payment_phone": payment_instance['contact'],
            "currency": payment_instance['currency'],
            "is_international": payment_instance['international'],
            "method": payment_instance['method'],
            "status": payment_instance['status'],
            "error_description": "",
            "refund_amount": 0,
            "user_id": None,
            "payment_page_url": order_notes['payment_page_url'],
            "grace_period": 0,
            "type": TransactionType.PAYMENT_PAGE,
            "shared_by": None,
            "payment_name": order_notes['payment_name']
        }

        if payment_instance['error_description'] is not None:
            transaction_data["error_description"] = payment_instance['error_description']

        if 'renew' in order_notes and order_notes['renew'] == "true":
            transaction_data['renew'] = True

        if 'amount' in refund_instance:
            transaction_data['refund_amount'] = refund_instance['amount']

        if 'user_id' in order_notes:
            transaction_data['user_id'] = order_notes['user_id']

        if 'shared_by' in order_notes:
            transaction_data['shared_by'] = order_notes['shared_by']

        if 'grace_period' in order_notes:
            transaction_data['grace_period'] = order_notes['grace_period']

        return transaction_data

    @staticmethod
    def _fetch_transaction_data_for_community_and_event(order_notes, payment_instance, refund_instance):
        transaction_data_list = []
        event_transaction_data = TransactionImpl._fetch_transaction_data_for_event(order_notes, payment_instance,
                                                                                   refund_instance)

        community_transaction_data = TransactionImpl._fetch_transaction_data_for_community_subscription(order_notes,
                                                                                                        payment_instance,
                                                                                                        refund_instance)
        transaction_data_list.append(event_transaction_data)
        transaction_data_list.append(community_transaction_data)

        return transaction_data_list

    @staticmethod
    def _attend_event_for_paid_transaction(transaction_instance):

        event_plan_id = transaction_instance.plan_id
        event_plan_instance = SubscriptionEventPlan.get_event_plan_or_None(event_plan_id)

        if not event_plan_instance:
            return

        chatroom_id = event_plan_instance.chatroom_id
        CoreServiceUtilities.attend_event({'chatroom_id': chatroom_id,
                                           'attending_status': True,
                                           'member_id': transaction_instance.user_id})

    def _create_transaction_data(self, transaction_body):
        payment_instance = transaction_body['payload']['payment']['entity']
        refund_instance = {}

        if 'refund' in transaction_body['payload']:
            refund_instance = transaction_body['payload']['refund']['entity']

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.fetch(payment_instance['order_id'])

        if not order_instance:
            return {'error_message': 'no order exists for given payment'}

        order_notes = order_instance['notes']
        is_event_transaction = order_notes['type'] == "event"
        is_community_and_event_transaction = order_notes['type'] == "community_and_event"
        is_payment_page_transaction = order_notes['type'] == 'payment_page'

        if is_payment_page_transaction:
            transaction_data = self._fetch_transaction_data_for_payment_page(order_notes, payment_instance,
                                                                             refund_instance)

            transaction_data_list = [transaction_data]

        elif is_community_and_event_transaction:
            transaction_data_list = self._fetch_transaction_data_for_community_and_event(order_notes, payment_instance,
                                                                                         refund_instance)
        elif is_event_transaction:
            transaction_data = self._fetch_transaction_data_for_event(order_notes, payment_instance, refund_instance)
            transaction_data_list = [transaction_data]

        else:
            transaction_data = self._fetch_transaction_data_for_community_subscription(order_notes,
                                                                                       payment_instance,
                                                                                       refund_instance)
            transaction_data_list = [transaction_data]

        return transaction_data_list

    @staticmethod
    def _create_member_acquisition_data(transaction_instance: Transaction, transaction_data: dict) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(transaction_data['plan_id'])

        acquisition_data = {
            'link_type': 'paid',
            'user_id': transaction_instance.user_id,
            'community_id': plan_instance.community_id if plan_instance is not None else None,
            'transaction_id': transaction_instance.id,
            'utm_source': None,
            'utm_campaign': None,
            'utm_medium': None,
            'utm_term': None,
            'utm_content': None,
            'shared_by': None
        }

        payment_page_string = transaction_instance.payment_page_url.split('?')

        if len(payment_page_string) > 1:

            params = {}

            params_strings = payment_page_string[1].split('&')

            for param_string in params_strings:
                param = param_string.split('=')
                params[param[0]] = param[1]

            if 'utm_source' in params:
                acquisition_data['utm_source'] = params['utm_source']

            if 'utm_campaign' in params:
                acquisition_data['utm_campaign'] = params['utm_campaign']

            if 'utm_medium' in params:
                acquisition_data['utm_medium'] = params['utm_medium']

            if 'utm_term' in params:
                acquisition_data['utm_term'] = params['utm_term']

            if 'utm_content' in params:
                acquisition_data['utm_content'] = params['utm_content']

            if 'shared_by' in params:
                acquisition_data['shared_by'] = params['shared_by']

        return acquisition_data

    @staticmethod
    def _send_analytics_for_membership_refund(transaction_instance):

        community_data = CoreServiceUtilities.get_community_data(transaction_instance.type_id)

        if 'community' in community_data and transaction_instance.user_id:
            analytics_data = {
                'community_id': transaction_instance.type_id,
                'community_name': community_data['community'].get('name'),
                'member_email': transaction_instance.payment_email,
                'member_phone': transaction_instance.payment_phone,
                'amount': NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount),
                'payment_id': transaction_instance.payment_id
            }

            analytics.track(transaction_instance.user_id, 'Membership transaction refunded (Backend)', analytics_data)

    def create_transaction(self) -> dict:

        transaction_raw_body = self.get_transaction_raw_body()
        transaction_signature = self.get_transaction_signature()
        transaction_body = self.get_transaction_body()

        signature_verification = self._verify_transaction_signature(transaction_raw_body, transaction_signature)

        if 'error_message' in signature_verification:
            return {'error_message': signature_verification['error_message']}

        existing_transaction_list = Transaction.get_transaction_list_or_None(
            transaction_body['payload']['payment']['entity']['id']
        )

        for existing_transaction_instance in existing_transaction_list:

            if existing_transaction_instance and \
                    existing_transaction_instance.type == TransactionType.COMMUNITY_SUBSCRIPTION:

                plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=existing_transaction_instance.plan_id)

                if transaction_body["event"] == "refund.processed":
                    existing_transaction_instance.status = "refund"
                    existing_transaction_instance.save()

                    self._send_analytics_for_membership_refund(existing_transaction_instance)

                    if existing_transaction_instance.user_id is not None:
                        subscription_instance = Subscription.get_subscription_or_None(
                            existing_transaction_instance.user_id, plan_instance.community_id)

                        if subscription_instance is not None:
                            current_time = TimeUtilities.current_time_in_milliseconds()
                            subscription_instance.valid_till = current_time
                            subscription_instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(
                                subscription_instance.valid_till, NOTIFY_PERIOD)
                            subscription_instance.save()

                        subscription_history_instance = SubscriptionHistory.objects.get(
                            transaction=existing_transaction_instance)

                        if subscription_history_instance is not None:
                            subscription_history_instance.type = 'refunded'
                            subscription_history_instance.save()

                    return {'success': True}

                else:

                    return {'error_message': 'transaction exists with given plan_id'}

            elif existing_transaction_instance and \
                    existing_transaction_instance.type == TransactionType.PAYMENT_PAGE:

                if transaction_body["event"] == "refund.processed":
                    existing_transaction_instance.status = "refund"
                    existing_transaction_instance.save()

                    return {'success': True}

                else:
                    return {'error_message': 'transaction exists with given plan_id'}

        transaction_data_list = self._create_transaction_data(transaction_body)

        for transaction_data in transaction_data_list:

            if 'error_message' in transaction_data:
                return {'error_message': transaction_data['error_message']}

            # What if one transaction is created but other could not be created
            transaction_instance = Transaction.create_instance(transaction_data)

            if not transaction_instance:
                return {'error_message': 'error while creating transaction'}

            if transaction_body['event'] == 'payment.captured' and \
                    transaction_instance.type == TransactionType.COMMUNITY_SUBSCRIPTION:

                if transaction_data['renew'] and transaction_data['user_id'] is not None:

                    subscription_manager = SubscriptionImpl(payment_id=transaction_data['payment_id'],
                                                            member_id=transaction_data['user_id'])

                    create_subscription = subscription_manager.create_subscription()

                    if 'error_message' in create_subscription:
                        return {'error_message': create_subscription['error_message']}

                    plan_instance = SubscriptionPlan.get_plan_or_None(transaction_instance.plan_id)

                    response = CoreServiceUtilities.renew_member(plan_instance.community_id,
                                                                 transaction_data['user_id'])

                    if 'error_message' in response:
                        return {'error_message': response['error_message']}

                if not transaction_data['renew'] and transaction_data['user_id'] is None:
                    acquisition_data = self._create_member_acquisition_data(transaction_instance, transaction_data)

                    MemberAcquisition.create_instance(acquisition_data)

                    # send join community communication
                    payment_success_membership_join_communication.delay(transaction_instance.id)

            if transaction_instance.type == TransactionType.EVENT and transaction_instance.user_id:

                if transaction_instance.status == 'captured':
                    self._attend_event_for_paid_transaction(transaction_instance)

                TransactionHelper.send_analytics_for_event_transaction.delay(transaction_instance.id)

            if transaction_instance.type == TransactionType.PAYMENT_PAGE:

                if transaction_instance.status == 'captured':

                    # Send Payment Page member success email and whatsapp
                    payment_page_member_payment_success_email.delay(transaction_instance.id)

                    # Send Payment Page CM success email
                    payment_page_cm_payment_success_email.delay(transaction_instance.id)

                elif transaction_instance.status == 'failed':

                    # Send Payment Page member success email and whatsapp
                    payment_page_member_payment_failed_email.delay(transaction_instance.id)

        return {'success': True}

    @staticmethod
    def _serialize_transactions(transactions):
        return TransactionSerializer(transactions)

    def fetch_transactions(self, page, payment_page_id=None, filters=None, settlement_id=None,
                           transaction_type=None) -> dict:

        if settlement_id:
            filters['settlement_id'] = settlement_id

        elif payment_page_id:
            filters['plan_id'] = payment_page_id

        else:
            if not transaction_type and self.get_user_id():
                filters['user_id'] = self.get_user_id()

            elif transaction_type and transaction_type == 'unidentified':
                filters['user_id'] = None

            elif transaction_type and transaction_type == 'all':
                pass

            valid_subscription_plan_ids = list(ModelUtilities.get_model_filter(
                SubscriptionPlan, {'community_id': self.get_community_id()}).values_list('plan_id', flat=True))

            valid_event_plan_ids = list(ModelUtilities.get_model_filter(
                SubscriptionEventPlan, {'community_id': self.get_community_id()}).values_list('event_plan_id',
                                                                                              flat=True))

            valid_payment_page_ids = list(ModelUtilities.get_model_filter(
                PaymentPageMeta, {'community_id': self.get_community_id()}).values_list('payment_page_id', flat=True))

            filters['plan_id__in'] = valid_subscription_plan_ids + valid_event_plan_ids + valid_payment_page_ids

        transactions = TransactionHelper.fetch_payment_transactions(filters)

        if len(transactions) == 0:
            return {'error_message': 'no transaction exist for given data in this community'}

        paginated_transactions = ModelUtilities.paginate_queryset(transactions, page, TRANSACTIONS_PAGE_SIZE)

        captured_transactions = [transaction for transaction in transactions if
                                 transaction.status == PAYMENTS_STATUS_FILTER['CAPTURED']]

        refunded_transactions = [transaction for transaction in transactions if
                                 transaction.status == PAYMENTS_STATUS_FILTER['REFUNDED']]

        return {'transactions': self._serialize_transactions(paginated_transactions),
                'captured_count': len(captured_transactions),
                'refunded_count': len(refunded_transactions)}

    def refund_transaction(self) -> dict:

        razorpay_client = RazorpayWrapper.get_instance()
        transaction_instance = self.get_transaction_instance()

        try:
            response = razorpay_client.payment.refund(transaction_instance.payment_id, transaction_instance.amount)
        except razorpay.errors.BadRequestError as e:
            return {'error_message': e.__str__()}

        return response

    def valid_event_transaction(self, chatroom_id, user_id) -> dict:

        event_plans_list = list(ModelUtilities.get_model_filter(SubscriptionEventPlan,
                                                                {'chatroom_id': chatroom_id}).
                                values_list('event_plan_id', flat=True))

        if not event_plans_list:
            return {'error_message': "No event plan exists"}

        has_transaction = ModelUtilities.get_model_filter(Transaction,
                                                          {'plan_id__in': event_plans_list,
                                                           'user_id': user_id})

        if has_transaction:
            return {'success': True}

        return {'success': False, 'error_message': "Invalid transaction"}

    def valid_event_payment_id(self, payment_id, user_id) -> dict:

        transaction_filter = ModelUtilities.get_model_filter(Transaction, {'payment_id': payment_id})

        if transaction_filter:
            transaction_instance = transaction_filter[0]

            if not transaction_instance.user_id:
                return {'success': True}

            if transaction_instance.user_id == NumberUtilities.get_integer_from_string(user_id):
                return {'success': True}

            else:
                return {'success': False, 'error_message': "Already used payment id"}

        else:

            return {'success': False, 'error_message': "In-valid payment id"}

    def update_payment_id(self, req_body, user_id) -> dict:

        transaction_filter = ModelUtilities.get_model_filter(Transaction, {'payment_id': req_body.get('payment_id')})

        if transaction_filter:
            transaction_instance = transaction_filter[0]

            if not transaction_instance.user_id:
                transaction_instance.user_id = user_id
                transaction_instance.save()

                return {'success': True}

            else:

                return {'success': False, 'error_message': "Already used payment id"}

        return {'success': False, 'error_message': "In-valid payment id"}

    def download_all_transaction(self, req_body, user_id) -> dict:

        payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                              {'payment_page_id': req_body.get('payment_page_id')})

        if not payment_page_filter:
            return {'error_message': 'Invalid payment_page_id', 'status_code': status_codes.HTTP_400_BAD_REQUEST}

        payment_page_instance = payment_page_filter[0]

        transactions_filter = TransactionHelper.fetch_payment_transactions(req_body.get('payment_page_id'))

        transaction_serialized_object = self._serialize_transactions(transactions_filter)

        if not transactions_filter:
            return {'error_message': 'No data found!', 'status_code': status_codes.HTTP_404_NOT_FOUND}

        transactions_df = CsvUtilities().object_list_to_dataframe(transaction_serialized_object)

        transactions_df = transactions_df.assign(status_text=transactions_df['status'].apply(
            lambda x: PAYMENTS_STATUS_MAPPER[x.upper()] if not pd.isnull(x) else ""))

        transactions_df['status'] = transactions_df['status_text']
        transactions_df['amount'] = transactions_df['amount'].apply(lambda x: NumberUtilities.convert_to_rupee_or_none(x))
        transactions_df.rename(columns=TRANSACTION_DOWNLOAD_ALL_PAYMENT_PAGE_CSV_COLUMN_MAPPER, inplace=True)
        transactions_df = transactions_df[TRANSACTION_DOWNLOAD_ALL_CSV_COLUMN_ORDERING_PAYMENT_PAGE_ID]

        transactions_df['Created On'] = transactions_df['Created On'].apply(
            lambda x: TimeUtilities.convert_epoch_time_to_date_month_year(x) + "\n" +
                      TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(x))

        file_name = TRANSACTION_DOWNLOAD_ALL_PAYMENT_PAGE_FILE_NAME.format(
            "_".join(payment_page_instance.title.split(" ")), time.strftime("%d-%m-%Y", time.localtime(time.time())))

        upload_status = S3Wrapper.upload_csv_file_and_get_link(transactions_df,
                                                               dir_path='utilities/payment_page_transaction_files',
                                                               file_name=file_name)

        if 'error_message' in upload_status:
            return {'success': False, 'error_message': upload_status['error_message'],
                    'status_code': status_codes.HTTP_408_REQUEST_TIMEOUT}

        # Get Owner of community
        community_owner_details = CoreServiceUtilities.get_community_admins(payment_page_instance.community_id,
                                                                            fetch_owner_only=True)

        if not community_owner_details:
            return {'error_message': "No owner found for the community",
                    'status_code': status_codes.HTTP_404_NOT_FOUND}

        community_owner_details = community_owner_details[0]

        user_verified_mobile_and_email = PaymentPageViewHelper.get_first_verified_email_and_phone(user_id)

        # Send Email
        mail_template = get_template("transactions_all_payment_page_download_report_mail.html").render(
            {"link": upload_status['link'],
             "cm_name": community_owner_details['name'],
             "payment_page_title": payment_page_instance.title})

        transaction_payment_page_mail_body = TRANSACTION_DOWNLOAD_ALL_PAYMENT_PAGEREPORT_TO_CM_BODY.copy()

        transaction_payment_page_mail_body['mail_body'] = mail_template
        transaction_payment_page_mail_body['mail_recipient_list'] = [user_verified_mobile_and_email['email']]

        send_email_response = send_email_from_core_service(user_id, transaction_payment_page_mail_body)

        return send_email_response

    @staticmethod
    def get_settlement_amount_data(community_id):

        community_data = CoreServiceUtilities.get_community_data(community_id)

        if 'error_message' in community_data:
            return ResponseUtilities.get_impl_error_context(community_data['error_message'],
                                                            status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

        community_details = community_data.get('community')
        fee_membership = community_details.get('fee_membership')
        fee_event = community_details.get('fee_event')
        fee_payment_pages = community_details.get('fee_payment_pages')

        valid_settlement_states = [SettlementStatus.FAILED, SettlementStatus.REVERSED]
        valid_settlements = ModelUtilities.get_model_filter(Settlement, {'community_id': community_id,
                                                                         'status__in': valid_settlement_states})

        valid_settlement_ids = [settlement.settlement_id for settlement in valid_settlements]

        subscription_and_payment_pages_transactions = (
                ModelUtilities.get_model_filter(Transaction, {'settlement_id__in': valid_settlement_ids,
                                                              'type_id': community_id,
                                                              'type__in': [TransactionType.PAYMENT_PAGE,
                                                                           TransactionType.COMMUNITY_SUBSCRIPTION],
                                                              'status': PAYMENTS_STATUS_FILTER['CAPTURED']
                                                              }).exclude(method__in=CASH_PAYMENT_STATUS) |
                ModelUtilities.get_model_filter(Transaction, {'settlement_id__isnull': True,
                                                              'type_id': community_id,
                                                              'type__in': [TransactionType.PAYMENT_PAGE,
                                                                           TransactionType.COMMUNITY_SUBSCRIPTION],
                                                              'status': PAYMENTS_STATUS_FILTER['CAPTURED']
                                                              }).exclude(method__in=CASH_PAYMENT_STATUS)
        ).values('type').annotate(revenue=Sum('amount'), count=Count('type'), start_date=Min('created_at'))

        subscription_and_payment_pages_refund_transactions = (
            ModelUtilities.get_model_filter(Transaction, {'settlement_id__isnull': False,
                                                          'status': PAYMENTS_STATUS_FILTER['REFUNDED'],
                                                          'refund_handled': TransactionRefundState.NOT_HANDLED,
                                                          'type_id': community_id,
                                                          'type__in': [TransactionType.PAYMENT_PAGE,
                                                                       TransactionType.COMMUNITY_SUBSCRIPTION]
                                                          })
        ).values('type').annotate(revenue=Sum('amount'), count=Count('type'))

        valid_event_plans = ModelUtilities.get_model_filter(SubscriptionEventPlan, {'community_id': community_id})

        valid_event_plan_ids = [plan.event_plan_id for plan in valid_event_plans]

        event_transactions = (
            ModelUtilities.get_model_filter(Transaction, {'settlement_id__in': valid_settlement_ids,
                                                          'plan_id__in': valid_event_plan_ids,
                                                          'type': TransactionType.EVENT,
                                                          'status': PAYMENTS_STATUS_FILTER['CAPTURED']
                                                          }) |
            ModelUtilities.get_model_filter(Transaction, {'settlement_id__isnull': True,
                                                          'plan_id__in': valid_event_plan_ids,
                                                          'type': TransactionType.EVENT,
                                                          'status': PAYMENTS_STATUS_FILTER['CAPTURED']
                                                          })
        ).values('type').annotate(revenue=Sum('amount'), count=Count('type'), start_date=Min('created_at'))

        event_refund_transactions = (
            ModelUtilities.get_model_filter(Transaction, {'settlement_id__isnull': False,
                                                          'status': PAYMENTS_STATUS_FILTER['REFUNDED'],
                                                          'refund_handled': TransactionRefundState.NOT_HANDLED,
                                                          'type': TransactionType.EVENT,
                                                          'plan_id__in': valid_event_plan_ids})
        ).values('type').annotate(revenue=Sum('amount'), count=Count('type'))

        membership_data = subscription_and_payment_pages_transactions.filter(
            type=TransactionType.COMMUNITY_SUBSCRIPTION)
        membership_refund_data = subscription_and_payment_pages_refund_transactions.filter(
            type=TransactionType.COMMUNITY_SUBSCRIPTION)
        payment_pages_data = subscription_and_payment_pages_transactions.filter(
            type=TransactionType.PAYMENT_PAGE)
        payment_pages_refund_data = subscription_and_payment_pages_refund_transactions.filter(
            type=TransactionType.PAYMENT_PAGE
        )
        event_data = event_transactions
        event_refund_data = event_refund_transactions

        revenue_membership = membership_data[0]['revenue'] if len(membership_data) else 0
        revenue_event = event_data[0]['revenue'] if len(event_data) else 0
        revenue_payment_pages = payment_pages_data[0]['revenue'] if len(payment_pages_data) else 0

        revenue_membership_refund = membership_refund_data[0]['revenue'] if len(membership_refund_data) else 0
        revenue_event_refund = event_refund_data[0]['revenue'] if len(event_refund_data) else 0
        revenue_payment_pages_refund = payment_pages_refund_data[0]['revenue'] if len(payment_pages_refund_data) else 0

        final_revenue_membership = revenue_membership - revenue_membership_refund
        final_revenue_event = revenue_event - revenue_event_refund
        final_revenue_payment_pages = revenue_payment_pages - revenue_payment_pages_refund

        revenue = final_revenue_membership + final_revenue_event + final_revenue_payment_pages

        count_membership = membership_data[0]['count'] if len(membership_data) else 0
        count_event = event_data[0]['count'] if len(event_data) else 0
        count_payment_pages = payment_pages_data[0]['count'] if len(payment_pages_data) else 0

        count = count_membership + count_event + count_payment_pages

        paid_amount = sum([(1-(fee_membership/100))*final_revenue_membership,
                           (1-(fee_event/100))*final_revenue_event,
                           (1-(fee_payment_pages/100))*final_revenue_payment_pages])

        fee_amount = revenue - paid_amount
        fee_amount_percent = (fee_amount/revenue)*100 if revenue > 0 else (fee_membership+fee_event+fee_payment_pages)/3

        data = {
            'revenue': revenue,
            'paid_amount': round(paid_amount),
            'fee_percentage': round(fee_amount_percent, 1),
            'fee_amount': round(fee_amount),
            'revenue_count': count,
            'start_epoch': min(membership_data[0]['start_date'] if len(membership_data) else LIFETIME_VALID_TILL,
                               event_data[0]['start_date'] if len(event_data) else LIFETIME_VALID_TILL,
                               payment_pages_data[0]['start_date'] if len(payment_pages_data) else LIFETIME_VALID_TILL)
        }

        return data

    @staticmethod
    def get_revenue_data(community_id):

        valid_event_plans = ModelUtilities.get_model_filter(SubscriptionEventPlan, {'community_id': community_id})

        valid_event_plan_ids = [plan.event_plan_id for plan in valid_event_plans]

        revenue_transactions = (
                ModelUtilities.get_model_filter(Transaction, {'type_id': community_id,
                                                              'type__in': [TransactionType.PAYMENT_PAGE,
                                                                           TransactionType.COMMUNITY_SUBSCRIPTION],
                                                              'status__in': [PAYMENTS_STATUS_FILTER['CAPTURED'],
                                                                             PAYMENTS_STATUS_FILTER['REFUNDED']]
                                                              }) |
                ModelUtilities.get_model_filter(Transaction, {'plan_id__in': valid_event_plan_ids,
                                                              'type': TransactionType.EVENT,
                                                              'status__in': [PAYMENTS_STATUS_FILTER['CAPTURED'],
                                                                             PAYMENTS_STATUS_FILTER['REFUNDED']]
                                                              })
        )

        total_revenue_details = revenue_transactions.filter(
            status=PAYMENTS_STATUS_FILTER['CAPTURED']
        ).aggregate(revenue=Sum('amount'))

        total_revenue_amount = total_revenue_details.get('revenue') if total_revenue_details.get('revenue') else 0

        current_date = TimeUtilities.get_current_date()
        date_epoch = TimeUtilities.convert_date_to_epoch(DAY_OF_MONTH_FOR_REVENUE_CALCULATION,
                                                         current_date.get('month'), current_date.get('year'))

        revenue_current_month = revenue_transactions.filter(status=PAYMENTS_STATUS_FILTER['CAPTURED'],
                                                            created_at__gte=date_epoch
                                                            ).aggregate(revenue=Sum('amount'))
        refund_current_month = revenue_transactions.filter(status=PAYMENTS_STATUS_FILTER['REFUNDED'],
                                                           refund_handled=TransactionRefundState.NOT_HANDLED,
                                                           settlement_id__isnull=False
                                                           ).aggregate(revenue=Sum('amount'))

        current_month_revenue = revenue_current_month.get('revenue') if revenue_current_month.get('revenue') else 0
        current_month_refund = refund_current_month.get('revenue') if refund_current_month.get('revenue') else 0

        data = {
            'total_revenue': total_revenue_amount,
            'revenue_current_month': current_month_revenue - current_month_refund
        }

        return data

    def fetch_settlement_amount(self) -> dict:

        settlement_data = self.get_settlement_amount_data(self.get_community_id())
        revenue_data = self.get_revenue_data(self.get_community_id())

        output_data = {
            'revenue': settlement_data.get('revenue'),
            'paid_amount': settlement_data.get('paid_amount'),
            'fee_percentage': settlement_data.get('fee_percentage'),
            'fee_amount': settlement_data.get('fee_amount'),
            'revenue_count': settlement_data.get('revenue_count'),
            'total_revenue': revenue_data.get('total_revenue'),
            'revenue_current_month': revenue_data.get('revenue_current_month')
        }

        return {'settlement_data': output_data}

    def create_free_transaction(self):
        transaction_body = self.get_transaction_body()
        plan_id = transaction_body.get('plan_id')
        shared_by = transaction_body.get('shared_by')
        plan_filter = ModelUtilities.get_model_filter(SubscriptionPlan, {'plan_id': plan_id})

        if not plan_filter:
            return {'error_message': "Invalid parameter: plan_id"}

        plan_instance = plan_filter[0]
        shared_by_member_state = CoreServiceUtilities.get_member_state(community_id=plan_instance.community_id,
                                                                       member_id=shared_by)

        if isinstance(shared_by_member_state, dict) and 'error_message' in shared_by_member_state:
            return ResponseUtilities.get_inner_error_context(shared_by_member_state['error_message'])

        if shared_by_member_state != MemberState.ADMIN:
            return ResponseUtilities.get_inner_error_context("Only CM can invite for free trial/lifetime plan!")

        transaction_exists = TransactionHelper.check_if_free_transaction_exists(plan_instance.community_id,
                                                                                transaction_body.get('payment_phone'))

        if transaction_exists:
            return ResponseUtilities.get_inner_error_context("Free trial can be subscribed only once!")

        transaction_data = TransactionHelper.create_transaction_object(plan_id=plan_id,
                                                                       amount=plan_instance.cost,
                                                                       email=transaction_body.get('payment_email'),
                                                                       phone=transaction_body.get('payment_phone'),
                                                                       type_id=TransactionType.COMMUNITY_SUBSCRIPTION,
                                                                       community_id=plan_instance.community_id,
                                                                       payment_page_url=transaction_body.get(
                                                                           'payment_page_url'),
                                                                       shared_by=transaction_body.get('shared_by'),
                                                                       free_transaction=True)
        transaction_instance = Transaction.create_instance(transaction_data)

        if not transaction_instance:
            return ResponseUtilities.get_inner_error_context("error while creating transaction")

        if transaction_data['renew'] and transaction_data['user_id'] is not None:

            subscription_manager = SubscriptionImpl(payment_id=transaction_data['payment_id'],
                                                    member_id=transaction_data['user_id'])

            create_subscription = subscription_manager.create_subscription()

            if 'error_message' in create_subscription:
                return ResponseUtilities.get_inner_error_context(create_subscription['error_message'])

            plan_instance = SubscriptionPlan.get_plan_or_None(transaction_instance.plan_id)

            response = CoreServiceUtilities.renew_member(plan_instance.community_id,
                                                         transaction_data['user_id'])

            if 'error_message' in response:
                return ResponseUtilities.get_inner_error_context(response['error_message'])

        if not transaction_data['renew'] and transaction_data['user_id'] is None:
            acquisition_data = self._create_member_acquisition_data(transaction_instance, transaction_data)

            MemberAcquisition.create_instance(acquisition_data)

            # send join community communication
            payment_success_membership_join_communication.delay(transaction_instance.id)

        return {'success': True, 'transaction_id': transaction_instance.id}


class TransactionHelper:

    @staticmethod
    def create_event_metadata(chatroom_data, cost_list):
        event_metadata = {
            'event_id': chatroom_data.get('id'),
            'community_id': chatroom_data.get('community_id'),
            'community_name': chatroom_data.get('community_name'),
            'event_name': chatroom_data.get('header'),
            'event_date': TimeUtilities.convert_epoch_time_to_date_month_year(chatroom_data.get('date_time')),
            'event_time': TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(chatroom_data.get('date_time')),
            'event_type': "paid" if chatroom_data.get('is_paid') else "free",
            'event_link': CHATROOM_LINK % (settings.URL, str(chatroom_data.get('id'))),
            'event_cost': cost_list
        }

        return event_metadata

    @staticmethod
    def compute_event_metadata_for_analytics(chatroom_id, user_id):

        chatroom_data = CoreServiceUtilities.chatroom_fetch({'chatroom_id': chatroom_id,
                                                             'member_id': user_id}).get('chatroom')

        if not chatroom_data or chatroom_data.get('error_message'):
            return

        event_filter = ModelUtilities.get_model_filter(SubscriptionEventPlan, {'chatroom_id': chatroom_id})
        cost_list = [plan_instance.cost / 100 for plan_instance in event_filter]

        event_metadata = TransactionHelper.create_event_metadata(chatroom_data, cost_list)

        return event_metadata

    @staticmethod
    @shared_task
    def send_analytics_for_event_transaction(transaction_id):

        transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

        if not transaction_instance:
            return

        if transaction_instance.status == 'captured':
            event_name = "Event payment successful (Subscription Service)"

        elif transaction_instance.status == 'failed':
            event_name = "Event payment failed (Subscription Service)"

        elif transaction_instance.status == 'refund':
            event_name = "Event payment refunded (Subscription Service)"

        else:
            return

        event_plan_id = transaction_instance.plan_id
        event_plan_instance = SubscriptionEventPlan.get_event_plan_or_None(event_plan_id)

        if not event_plan_instance:
            return

        chatroom_id = event_plan_instance.chatroom_id
        user_id = transaction_instance.user_id

        event_metadata = TransactionHelper.compute_event_metadata_for_analytics(chatroom_id, user_id)
        SegmentImpl.track_event(user_id, event_name, event_metadata)

    @staticmethod
    def fetch_payment_transactions(filters):
        transactions = ModelUtilities.get_model_filter(Transaction, filters).order_by('-created_at')

        return transactions

    @staticmethod
    def get_payment_id_and_method_for_transaction(transaction_type_id):

        unique_id = uuid.uuid4()
        payment_id = 'mig_{}'.format(unique_id)
        method = MIGRATION

        if transaction_type_id == TransactionType.PAYMENT_PAGE:
            payment_id = 'ppc_{}'.format(unique_id)
            method = MANUAL_PAYMENT_PAGE

        return payment_id, method

    @staticmethod
    def create_transaction_object(plan_id, amount, email, phone, type_id, community_id, payment_name: str = '',
                                  renew: bool = False, user_id: int = None, payment_page_url: str = '',
                                  shared_by: int = None, free_transaction: bool = False):

        payment_id, method = TransactionHelper.get_payment_id_and_method_for_transaction(type_id)
        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id)

        if plan_instance is None:

            if type_id != TransactionType.PAYMENT_PAGE:
                return {'error_message': 'invalid plan_id', 'status': status_codes.HTTP_400_BAD_REQUEST}

            plan_name, plan_cost = "", amount

        else:
            plan_name, plan_cost = plan_instance.name, plan_instance.cost

        community_data = CoreServiceUtilities.get_community_data(community_id)

        if 'error_message' in community_data:
            return {'error_message': community_data['error_message'],
                    'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

        transaction_data = {
            "buddy_emails": plan_instance.buddy_emails,
            "cm_emails": plan_instance.cm_emails,
            "community_name": community_data['community']['name'],
            "payment_page_url": payment_page_url,
            "plan_id": plan_id,
            "grace_period": 0,
            "shared_by": shared_by,
            "type": type_id,
            "payment_id": payment_id,
            "plan_name": plan_name,
            "plan_cost": plan_cost,
            "payment_email": email,
            "payment_phone": phone,
            "currency": "INR",
            "is_international": False,
            "method": method,
            "status": TransactionStatusType.CAPTURED,
            "renew": renew,
            "amount": amount,
            "error_description": "",
            "refund_amount": 0,
            "user_id": user_id,
            "type_id": community_id,
            "payment_name": payment_name
        }

        if free_transaction:
            transaction_data['grace_period'] = community_data['community']['grace_period']

        return transaction_data

    @staticmethod
    def check_if_free_transaction_exists(community_id, payment_phone):

        free_trial_plans = ModelUtilities.get_model_filter(SubscriptionPlan,
                                                           {'community_id': community_id, 'is_paid': False})

        plan_ids = list(free_trial_plans.exclude(duration_name=LIFETIME_PAYMENT).values_list('plan_id', flat=True))

        existing_free_transaction = ModelUtilities.is_model_filter_exists(Transaction,
                                                                          {'plan_id__in': plan_ids,
                                                                           'payment_phone': payment_phone})
        return existing_free_transaction
