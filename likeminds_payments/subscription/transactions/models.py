from django.db import models

from ..plans.models import SubscriptionEventPlan, SubscriptionPlan
from ..utility.states import TransactionType
from ..utility.time_utilities import TimeUtilities


class Transaction(models.Model):
    plan_id = models.CharField(max_length=64)
    payment_id = models.CharField(max_length=64)
    community_name = models.CharField(max_length=200)
    plan_name = models.CharField(max_length=128, null=True)
    plan_cost = models.IntegerField(default=0)
    renew = models.BooleanField(default=False)
    amount = models.IntegerField(default=0)
    payment_email = models.CharField(max_length=128)
    payment_phone = models.CharField(max_length=20)
    currency = models.CharField(max_length=3)
    is_international = models.BooleanField(default=False)
    method = models.CharField(max_length=64)
    status = models.CharField(max_length=8)
    error_description = models.TextField(default='')
    refund_amount = models.IntegerField(default=0)
    user_id = models.IntegerField(null=True, default=None)
    payment_page_url = models.CharField(max_length=1000)
    shared_by = models.IntegerField(null=True, default=None)
    grace_period = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    type_id = models.IntegerField(default=0)
    payment_name = models.TextField(default='')
    settlement_id = models.CharField(max_length=64, null=True, default=None)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.pk)

    @staticmethod
    def get_transaction_or_None(payment_id, transaction_type=TransactionType.COMMUNITY_SUBSCRIPTION):
        try:
            return Transaction.objects.get(payment_id=payment_id, type=transaction_type)
        except:
            return None

    @staticmethod
    def get_transaction_list_or_None(payment_id):
        return Transaction.objects.filter(payment_id=payment_id)

    @staticmethod
    def get_transaction_with_id_or_None(transaction_id):
        try:
            return Transaction.objects.get(pk=transaction_id)
        except:
            return None

    @staticmethod
    def create_instance(transaction_body):
        instance = Transaction()
        instance.plan_id = transaction_body['plan_id']
        instance.payment_id = transaction_body['payment_id']
        instance.community_name = transaction_body['community_name']
        instance.plan_name = transaction_body.get('plan_name')
        instance.plan_cost = transaction_body['plan_cost']
        instance.renew = transaction_body['renew']
        instance.amount = transaction_body['amount']
        instance.payment_email = transaction_body['payment_email']
        instance.payment_phone = transaction_body['payment_phone']
        instance.currency = transaction_body['currency']
        instance.is_international = transaction_body['is_international']
        instance.method = transaction_body['method']
        instance.status = transaction_body['status']
        instance.error_description = transaction_body['error_description']
        instance.refund_amount = transaction_body['refund_amount']
        instance.user_id = transaction_body['user_id']
        instance.payment_page_url = transaction_body['payment_page_url']
        instance.shared_by = transaction_body['shared_by']
        instance.grace_period = transaction_body['grace_period']
        instance.type = transaction_body.get('type', 0)
        instance.type_id = transaction_body.get('type_id', 0)
        instance.payment_name = transaction_body.get('payment_name', '')

        if instance.type == TransactionType.EVENT:
            event_plan_instance = SubscriptionEventPlan.get_event_plan_or_None(transaction_body['plan_id'])
            instance.type_id = event_plan_instance.chatroom_id

        if instance.type == TransactionType.COMMUNITY_SUBSCRIPTION:
            plan_instance = SubscriptionPlan.get_plan_or_None(transaction_body['plan_id'])
            instance.type_id = plan_instance.community_id

        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Transaction, self).save(*args, **kwargs)
