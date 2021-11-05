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
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return self.pk

    @staticmethod
    def create_instance(kyc_body):
        instance = CommunityKYC()
        instance.user_id = kyc_body.get('user_id')
        instance.community_id = kyc_body.get('community_id')
        instance.name = kyc_body.get('name', '')
        instance.address = kyc_body.get('address', '')
        instance.doc_type = kyc_body.get('doc_type', None)
        instance.doc_number = kyc_body.get('doc_number', None)
        instance.doc_front_url = kyc_body.get('doc_front_url', None)
        instance.doc_back_url = kyc_body.get('doc_back_url', None)
        instance.doc_pan_number = kyc_body.get('doc_pan_number', None)
        instance.doc_pan_url = kyc_body.get('doc_pan_url', None)
        instance.gstn = kyc_body.get('gstn', None)
        instance.bank_user_name = kyc_body.get('bank_user_name', '')
        instance.bank_ifsc_code = kyc_body.get('bank_ifsc_code', '')
        instance.account_number = kyc_body.get('account_number', None)
        instance.bank_name = kyc_body.get('bank_name', '')
        instance.status = KYCState.PENDING_APPROVAL
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(CommunityKYC, self).save(*args, **kwargs)

