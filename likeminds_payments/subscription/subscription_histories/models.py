from django.db import models
from ..transactions.models import Transaction
from ..utility.time_utilities import TimeUtilities


class SubscriptionHistory(models.Model):
    start_date = models.BigIntegerField(default=0)
    end_date = models.BigIntegerField(default=0)
    description = models.TextField(default='')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=8)
    user_id = models.IntegerField()
    community_id = models.IntegerField()
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
