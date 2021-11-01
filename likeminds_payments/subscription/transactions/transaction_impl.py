from __future__ import absolute_import, unicode_literals

import pandas as pd
from celery import shared_task
from .transaction_manager import TransactionManager
from django.conf import settings
from django.template.loader import get_template
import time
from rest_framework import status as status_codes
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper
from ..external_services.segment.segment_impl import SegmentImpl
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.states import TransactionType
from ..utility.time_utilities import TimeUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.async_tasks import (payment_page_member_payment_success_email, payment_page_member_payment_failed_email,
                                   payment_page_cm_payment_success_email, send_email_from_core_service,
                                   payment_success_membership_join_communication)
from ..utility.csv_utilities import CsvUtilities
from .constants import *
from .models import Transaction
from ..plans.models import SubscriptionPlan, SubscriptionEventPlan
from ..subscriptions.models import Subscription
from ..payment_page.models import PaymentPageMeta
from ..payment_page.payment_page_view_helper import PaymentPageViewHelper
from ..subscription_histories.models import SubscriptionHistory
from ..member_acquisition.models import MemberAcquisition
from ..subscriptions.subscription_view_impl import SubscriptionImpl
from .serializers import TransactionSerializer

from ..external_services.s3.s3_wrapper import S3Wrapper

import hmac
import hashlib
import razorpay


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
            "plan_id": order_notes['plan_id'],
            "payment_id": payment_instance['id'],
            "community_name": order_notes['community_name'],
            "plan_name": order_notes['name'],
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
            "payment_page_url": order_notes['payment_page_url'],
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

        if 'user_id' in order_notes:
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

    @staticmethod
    def _fetch_transactions(user_id: str, community_id: str):
        output = []

        transactions = ModelUtilities.get_model_filter(Transaction, {'user_id': user_id}).order_by('created_at')

        for transaction in transactions:
            plan = SubscriptionPlan.get_plan_or_None(transaction.plan_id)

            if plan is not None and plan.community_id == community_id:
                output.append(transaction)

        return output

    def fetch_transactions(self, page, payment_page_id=None) -> dict:

        transactions = []

        if payment_page_id:
            transactions = TransactionHelper.fetch_payment_transactions(payment_page_id)

        else:
            transactions = self._fetch_transactions(self.get_user_id(), self.get_community_id())

        if len(transactions) == 0:
            return {'error_message': 'no transaction exist for this user in this community'}

        paginated_transactions = ModelUtilities.paginate_queryset(transactions, page, PAGE_SIZE)

        return {'transactions': self._serialize_transactions(paginated_transactions)}

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
    def fetch_payment_transactions(payment_page_id):
        transactions = ModelUtilities.get_model_filter(Transaction,
                                                       {'plan_id': payment_page_id}).order_by('created_at')

        return transactions
