from django.db import models
import uuid
from ..utility.time_utilities import TimeUtilities


class SubscriptionPlan(models.Model):
    plan_id = models.CharField(unique=True, max_length=64)
    community_id = models.IntegerField(null=False)
    name = models.CharField(null=True, max_length=128)
    duration_name = models.CharField(max_length=16)
    cost = models.IntegerField(null=True)
    strike_cost = models.IntegerField(null=True)
    cost_usd = models.IntegerField(null=True)
    strike_cost_usd = models.IntegerField(null=True)
    duration_in_months = models.IntegerField()
    cm_emails = models.TextField(default='')
    buddy_emails = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(default='')
    referral_free_days = models.IntegerField(default=0)
    image = models.CharField(max_length=256)
    description_icon_type = models.IntegerField(null=True)
    is_paid = models.BooleanField(default=True)
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
        instance.strike_cost = plan_body['strike_cost']
        instance.cost_usd = plan_body['cost_usd']
        instance.strike_cost_usd = plan_body['strike_cost_usd']
        instance.duration_in_months = plan_body['duration_in_months']
        instance.cm_emails = plan_body['cm_emails']
        instance.buddy_emails = plan_body['buddy_emails']
        instance.is_deleted = False
        instance.description = plan_body['description']
        instance.referral_free_days = plan_body['referral_free_days']
        instance.image = plan_body['image']
        instance.description_icon_type = plan_body['description_icon_type']
        instance.is_paid = plan_body.get('is_paid', True)
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SubscriptionPlan, self).save(*args, **kwargs)


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
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

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
        instance.save()

        return instance

    @staticmethod
    def get_event_plan_or_None(plan_id):
        try:
            return SubscriptionEventPlan.objects.get(event_plan_id=plan_id)
        except:
            return None

    def save(self, *args, **kwargs):
        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SubscriptionEventPlan, self).save(*args, **kwargs)


class EventCohortPlan(models.Model):
    event_plan = models.ForeignKey(SubscriptionEventPlan, on_delete=models.CASCADE)
    cohort_id = models.IntegerField()
    cost = models.IntegerField(default=0)
    strike_cost = models.IntegerField(null=True)
    cost_usd = models.IntegerField(null=True)
    strike_cost_usd = models.IntegerField(null=True)
    discount_type = models.IntegerField(null=True)
    discount = models.IntegerField(null=True)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(EventCohortPlan, self).save(*args, **kwargs)

class SamplePlanCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    image_url = models.TextField()
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SamplePlanCategory, self).save(*args, **kwargs)


class SamplePlan(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.ForeignKey(SamplePlanCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_name = models.CharField(default="", max_length=255)
    duration_in_months = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    strike_cost = models.IntegerField(default=0)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(SamplePlan, self).save(*args, **kwargs)
