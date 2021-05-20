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
