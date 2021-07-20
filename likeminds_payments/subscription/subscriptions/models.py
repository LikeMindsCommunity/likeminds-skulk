import uuid

from django.db import models
from ..utility.time_utilities import TimeUtilities
from ..transactions.models import Transaction


class Subscription(models.Model):
    user_id = models.IntegerField()
    community_id = models.IntegerField()
    plan_id = models.CharField(max_length=64, null=True)
    date_subscribed = models.BigIntegerField(default=0)
    valid_till = models.BigIntegerField(default=0)
    date_unsubscribed = models.BigIntegerField(default=None, null=True)
    type = models.CharField(max_length=10)
    renewal_due = models.BigIntegerField(default=0)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)
    is_removed = models.BooleanField(default=False)
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
        instance.is_removed = False
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Subscription, self).save(*args, **kwargs)


class SubscriptionEventPlan(models.Model):
    event_plan_id = models.CharField(unique=True, max_length=64)
    chatroom_id = models.IntegerField()
    community_id = models.IntegerField()
    cost = models.IntegerField(default=0)
    strike_cost = models.IntegerField(null=True)
    cost_usd = models.IntegerField(null=True)
    strike_cost_usd = models.IntegerField(null=True)
    discount_type = models.IntegerField(null=True)
    discount = models.IntegerField(null=True)

    @staticmethod
    def create_instance(create_info):
        instance = SubscriptionEventPlan()
        instance.event_plan_id = str(uuid.uuid4())
        instance.chatroom_id = create_info.get('chatroom_id')
        instance.community_id = create_info.get('community_id')
        instance.cost = create_info.get('cost')
        instance.strike_cost = create_info.get('strike_cost')
        instance.cost_usd = create_info.get('cost_usd')
        instance.strike_cost_usd = create_info.get('strike_cost_usd')
        instance.discount_type = create_info.get('discount_type')
        instance.discount = create_info.get('discount')

        return instance

    def save(self, *args, **kwargs):
        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SubscriptionEventPlan, self).save(*args, **kwargs)
