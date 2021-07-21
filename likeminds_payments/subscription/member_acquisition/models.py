from django.db import models
from ..utility.time_utilities import TimeUtilities


class MemberAcquisition(models.Model):
    link_type = models.CharField(max_length=8)
    user_id = models.IntegerField()
    community_id = models.IntegerField()
    utm_source = models.CharField(max_length=128)
    utm_campaign = models.CharField(max_length=128)
    utm_medium = models.CharField(max_length=128)
    utm_term = models.CharField(max_length=128)
    utm_content = models.CharField(max_length=128)
    shared_by = models.IntegerField(null=True, default=None)
    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.pk)

    @staticmethod
    def get_member_acquisition_or_None(user_id, community_id):
        try:
            return MemberAcquisition.objects.get(user_id=user_id, community_id=community_id)
        except:
            return None

    @staticmethod
    def create_instance(member_acquisition_body):
        instance = MemberAcquisition()
        instance.link_type = member_acquisition_body['link_type']
        instance.user_id = member_acquisition_body['user_id']
        instance.community_id = member_acquisition_body['community_id']
        instance.utm_source = member_acquisition_body['utm_source']
        instance.utm_campaign = member_acquisition_body['utm_campaign']
        instance.utm_medium = member_acquisition_body['utm_medium']
        instance.utm_term = member_acquisition_body['utm_term']
        instance.utm_content = member_acquisition_body['utm_content']
        instance.shared_by = member_acquisition_body['shared_by']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        current_time = TimeUtilities.current_time_in_milliseconds()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(MemberAcquisition, self).save(*args, **kwargs)
