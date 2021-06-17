from django.db import models
import uuid
from ..utility.time_utilities import TimeUtilities


class SubscriptionPlan(models.Model):
    plan_id = models.CharField(unique=True, max_length=64)
    community_id = models.IntegerField(null=False)
    name = models.CharField(null=True, max_length=128)
    duration_name = models.CharField(max_length=16)
    cost = models.IntegerField(default=0)
    duration_in_months = models.IntegerField()
    cm_emails = models.TextField(default='')
    buddy_emails = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(default='')
    referral_free_days = models.IntegerField(default=0)
    image = models.CharField(max_length=256)
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
