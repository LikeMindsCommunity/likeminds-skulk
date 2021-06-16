from django.db import models
import uuid
from .utility.time_utilities import TimeUtilities


class SubscriptionPlan(models.Model):
    plan_id = models.CharField(unique=True, max_length=64)
    community_id = models.IntegerField(default=0)
    name = models.CharField(null=True, max_length=128)
    duration_name = models.CharField(max_length=16)
    cost = models.IntegerField(default=0)
    duration_in_months = models.IntegerField(default=0)
    cm_emails = models.TextField(null=True)
    buddy_emails = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(default='')
    referral_free_days = models.IntegerField(default=0)
    image = models.CharField(max_length=256, default='')
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.plan_id

    @staticmethod
    def get_plan_or_None(plan_id):
        try:
            return SubscriptionPlan.objects.get(plan_id=plan_id)
        except:
            return None

    @staticmethod
    def create_instance(plan_body):
        instance = SubscriptionPlan()
        instance.plan_id = str(uuid.uuid4())
        instance.community_id = plan_body['community_id']
        instance.name = plan_body['name']
        instance.duration_name = plan_body['duration_name']
        instance.cost = plan_body['cost']
        instance.duration_in_months = plan_body['duration_in_months']
        instance.cm_emails = plan_body['cm_emails']
        instance.buddy_emails = plan_body['buddy_emails']
        instance.is_deleted = False
        instance.description = plan_body['description']
        instance.referral_free_days = plan_body['referral_free_days']
        instance.image = plan_body['image']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SubscriptionPlan, self).save(*args, **kwargs)


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
    payment_page_url = models.CharField(max_length=256)
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
    def get_transaction_with_id_or_None(pk):
        try:
            return Transaction.objects.get(pk=pk)
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


class Subscription(models.Model):
    user_id = models.IntegerField(default=0)
    community_id = models.IntegerField(default=0)
    plan_id = models.CharField(max_length=64)
    date_subscribed = models.BigIntegerField(default=0)
    valid_till = models.BigIntegerField(default=0)
    date_unsubscribed = models.BigIntegerField(default=None, null=True)
    type = models.CharField(max_length=10)
    renewal_due = models.BigIntegerField(default=0)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.pk

    @staticmethod
    def get_subscription_or_None(user_id, community_id):
        try:
            return Subscription.objects.get(user_id=user_id, community_id=community_id)
        except:
            return None

    @staticmethod
    def create_instance(subscription_body):
        instance = Subscription()
        instance.user_id = subscription_body['user_id']
        instance.community_id = subscription_body['community_id']
        instance.plan_id = subscription_body['plan_id']
        instance.date_subscribed = subscription_body['date_subscribed']
        instance.valid_till = subscription_body['valid_till']
        instance.date_unsubscribed = None
        instance.type = subscription_body['type']
        instance.renewal_due = subscription_body['renewal_due']
        instance.transaction = subscription_body['transaction']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Subscription, self).save(*args, **kwargs)


class SubscriptionHistory(models.Model):
    start_date = models.BigIntegerField(default=0)
    end_date = models.BigIntegerField(default=0)
    description = models.TextField(default='')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=8)
    user_id = models.IntegerField(default=0)
    community_id = models.IntegerField(default=0)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.pk

    @staticmethod
    def get_history_with_transaction_or_None(transaction_instance):
        try:
            return Subscription.objects.get(transaction=transaction_instance)
        except:
            return None

    @staticmethod
    def create_instance(subscription_history_body):
        instance = SubscriptionHistory()
        instance.start_date = subscription_history_body['start_date']
        instance.end_date = subscription_history_body['end_date']
        instance.description = subscription_history_body['description']
        instance.transaction = subscription_history_body['transaction']
        instance.type = subscription_history_body['type']
        instance.user_id = subscription_history_body['user_id']
        instance.community_id = subscription_history_body['community_id']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SubscriptionHistory, self).save(*args, **kwargs)
