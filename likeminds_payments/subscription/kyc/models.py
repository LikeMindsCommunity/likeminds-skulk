from django.db import models
from ..utility.time_utilities import TimeUtilities
from ..utility.states import KYCState


class CommunityKYC(models.Model):
    user_id = models.IntegerField()
    community_id = models.IntegerField()
    name = models.CharField(max_length=128, default='')
    address = models.TextField(default='')
    doc_type = models.IntegerField(default=None, null=True)
    doc_number = models.CharField(max_length=128, default=None, null=True)
    doc_front_url = models.TextField(default=None, null=True)
    doc_back_url = models.TextField(default=None, null=True)
    doc_pan_number = models.CharField(max_length=16, default=None, null=True)
    doc_pan_url = models.TextField(default=None, null=True)
    gstn = models.CharField(max_length=32, default=None, null=True)
    bank_user_name = models.CharField(max_length=128, default='')
    bank_ifsc_code = models.CharField(max_length=16, default='')
    account_number = models.CharField(max_length=32, default=None, null=True)
    bank_name = models.CharField(max_length=128, default='')
    status = models.IntegerField(default=0)
    contact_id = models.CharField(max_length=64, default=None, null=True)
    account_id = models.CharField(max_length=64, default=None, null=True)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.pk

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(CommunityKYC, self).save(*args, **kwargs)

