from django.db import models
from ..utility.time_utilities import TimeUtilities


class Transaction(models.Model):
    plan_id = models.CharField(max_length=64)
    payment_id = models.CharField(unique=True, max_length=64)
    community_name = models.CharField(max_length=200)
    plan_name = models.CharField(max_length=128)
    plan_cost = models.IntegerField(default=0)
    renew = models.BooleanField(default=False)
    amount = models.IntegerField(default=0)
    payment_email = models.CharField(max_length=128)
    payment_phone = models.CharField(max_length=13)
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
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.pk)

    @staticmethod
    def get_transaction_or_None(payment_id):
        try:
            return Transaction.objects.get(payment_id=payment_id)
        except:
            return None

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
        instance.plan_name = transaction_body['plan_name']
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
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Transaction, self).save(*args, **kwargs)
