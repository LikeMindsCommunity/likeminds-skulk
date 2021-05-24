from django.db import models
import uuid
from .utility.time_utilities import TimeUtilities

# Create your models here.

plan_choices = (
    ('Monthly Membership', 'Monthly'),
    ('Quarterly Membership', 'Quarterly'),
    ('Half Yearly Membership', 'Half Yearly'),
    ('Yearly Membership', 'Yearly'),
)

plan_values = {
    'Monthly Membership': 1,
    'Quarterly Membership': 3,
    'Half Yearly Membership': 6,
    'Yearly Membership': 12
}


class Plans(models.Model):
    community_name = models.CharField(max_length=128)
    community_id = models.IntegerField()
    plan_name = models.CharField(choices=plan_choices, max_length=64)
    plan_cost = models.FloatField()
    plan_length = models.IntegerField()
    community_join_link = models.URLField()
    community_manager_mail = models.EmailField()
    community_buddy_mail = models.EmailField()
    plan_id = models.CharField(unique=True, max_length=64)

    def __str__(self):
        return self.plan_id

    @staticmethod
    def get_plan_or_None(plan_id):
        try:
            return Plans.objects.get(plan_id=plan_id)
        except:
            return None

    @staticmethod
    def get_plan_size():
        return len(Plans.objects.all())

    @staticmethod
    def create_instance(create_info):
        instance = Plans()
        instance.community_name = create_info['community_name']
        instance.community_id = create_info['community_id']
        instance.plan_name = create_info['plan_name']
        instance.plan_cost = create_info['plan_cost']
        instance.plan_length = plan_values[create_info['plan_name']]
        instance.community_join_link = create_info['community_join_link']
        instance.community_manager_mail = create_info['community_manager_mail']
        instance.community_buddy_mail = create_info['community_buddy_mail']
        instance.plan_id = str(uuid.uuid4())
        instance.save()

        return instance


class SubscriptionPlan(models.Model):
    plan_id = models.CharField(unique=True, max_length=64)
    community_id = models.IntegerField(default=0)
    name = models.CharField(null=True, max_length=128)
    duration_name = models.CharField(max_length=16)
    cost = models.IntegerField(default=0)
    duration_in_months = models.IntegerField(default=0)
    cm_emails = models.TextField(null=True)
    buddy_emails = models.TextField(null=True)
    trials = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
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
        instance.trials = plan_body['trials']
        instance.is_deleted = False
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
    payment_page_url = models.CharField(max_length=128)
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
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Transaction, self).save(*args, **kwargs)


class Subscription(models.Model):
    user_id = models.IntegerField()
    community_id = models.IntegerField(default=0)
    plan_id = models.CharField(max_length=64)
    date_subscribed = models.BigIntegerField(default=0)
    valid_till = models.BigIntegerField(default=0)
    date_unsubscribed = models.BigIntegerField(default=None, null=True)
    trial_end = models.BigIntegerField(default=None, null=True)
    type = models.CharField(max_length=10)
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
        instance.trial_end = subscription_body['trial_end']
        instance.type = subscription_body['type']
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
    status = models.CharField(max_length=8)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.pk

    @staticmethod
    def create_instance(subscription_history_body):
        instance = SubscriptionHistory()
        instance.start_date = subscription_history_body['start_date']
        instance.end_date = subscription_history_body['end_date']
        instance.description = subscription_history_body['description']
        instance.transaction = subscription_history_body['transaction']
        instance.type = subscription_history_body['type']
        instance.status = subscription_history_body['status']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SubscriptionHistory, self).save(*args, **kwargs)
