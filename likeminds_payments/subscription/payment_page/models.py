from django.db import models
import uuid
from ..utility.time_utilities import TimeUtilities


class PaymentPageMeta(models.Model):
    payment_page_id = models.CharField(unique=True, max_length=64)
    title = models.CharField(max_length=256)
    description = models.TextField(default='')
    amount_type = models.CharField(max_length=128)
    amount = models.FloatField(null=True)
    custom_success_message = models.TextField(null=True)
    redirect_url = models.TextField(null=True)
    community_id = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    contact_email = models.CharField(max_length=256)
    contact_mobile_no = models.CharField(max_length=128)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.payment_page_id

    @staticmethod
    def create_instance(plan_body):
        instance = PaymentPageMeta()
        instance.payment_page_id = str(uuid.uuid4())
        instance.title = plan_body['title']
        instance.description = plan_body['description']
        instance.amount_type = plan_body['amount_type']
        instance.amount = plan_body['amount']
        instance.custom_success_message = plan_body['custom_success_message']
        instance.redirect_url = plan_body['redirect_url']
        instance.community_id = plan_body['community_id']
        instance.is_active = plan_body['is_active']
        instance.contact_email = plan_body['contact_email']
        instance.contact_mobile_no = plan_body['contact_mobile_no']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(PaymentPageMeta, self).save(*args, **kwargs)
