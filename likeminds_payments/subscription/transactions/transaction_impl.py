from .transaction_manager import TransactionManager
from django.conf import settings
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.states import TransactionType
from ..utility.time_utilities import TimeUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from .constants import *
from .models import Transaction
from ..plans.models import SubscriptionPlan, SubscriptionEventPlan
from ..subscriptions.models import Subscription
from ..subscription_histories.models import SubscriptionHistory
from ..member_acquisition.models import MemberAcquisition
from ..subscriptions.subscription_view_impl import SubscriptionImpl
from .serializers import TransactionSerializer

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
            "type": TransactionType.EVENT
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
    def _attend_event_for_paid_transaction(transaction_instance):

        event_plan_id = transaction_instance.plan_id
        event_plan_instance = SubscriptionEventPlan.get_event_plan_or_None(event_plan_id)

        if not event_plan_instance:
            return

        chatroom_id = event_plan_id.chatroom_id
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

        if is_event_transaction:
            transaction_data = self._fetch_transaction_data_for_event(order_notes, payment_instance, refund_instance)

        else:
            transaction_data = self._fetch_transaction_data_for_community_subscription(order_notes,
                                                                                       payment_instance, refund_instance)

        return transaction_data

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

        existing_transaction_instance = Transaction.get_transaction_or_None(
            transaction_body['payload']['payment']['entity']['id']
        )

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

        transaction_data = self._create_transaction_data(transaction_body)

        if 'error_message' in transaction_data:
            return {'error_message': transaction_data['error_message']}

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

                response = CoreServiceUtilities.renew_member(plan_instance.community_id, transaction_data['user_id'])

                if 'error_message' in response:
                    return {'error_message': response['error_message']}

            if not transaction_data['renew'] and transaction_data['user_id'] is None:

                acquisition_data = self._create_member_acquisition_data(transaction_instance, transaction_data)

                MemberAcquisition.create_instance(acquisition_data)

        if transaction_instance.type == TransactionType.EVENT and transaction_instance.user_id:
            self._attend_event_for_paid_transaction(transaction_instance)

        return {'success': True}

    @staticmethod
    def _serialize_transactions(transactions):
        return TransactionSerializer(transactions)

    @staticmethod
    def _fetch_transactions(user_id: str, community_id: str):
        output = []
        transactions = Transaction.objects.filter(user_id=user_id).order_by('created_at')
        for transaction in transactions:
            plan = SubscriptionPlan.get_plan_or_None(transaction.plan_id)
            if plan is not None and plan.community_id == community_id:
                output.append(transaction)
        return output

    def fetch_transactions(self, page) -> dict:

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

        event_plan_id = SubscriptionEventPlan.get_event_plan_or_None(chatroom_id)

        if not event_plan_id:
            return {'error_message': "No event plan exists"}

        has_transaction = Transaction.objects.filter(plan_id=event_plan_id, user_id=user_id)

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
