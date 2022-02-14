from django.db import models
from ..utility.time_utilities import TimeUtilities


class Settlement(models.Model):
    settlement_id = models.CharField(max_length=64, unique=True, null=True)
    community_id = models.IntegerField()
    start_epoch = models.BigIntegerField()
    end_epoch = models.BigIntegerField()
    amount = models.IntegerField()
    currency = models.CharField(max_length=3, default='INR')
    status = models.IntegerField()
    fee_amount = models.IntegerField(null=True, default=None)
    fee_percentage = models.IntegerField(null=True, default=None)
    revenue = models.IntegerField(null=True, default=None)
    reference_id = models.CharField(max_length=64, unique=True)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Settlement, self).save(*args, **kwargs)

