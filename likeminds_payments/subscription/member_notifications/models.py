from django.db import models


class MemberNotification(models.Model):
    user_id = models.IntegerField()
    community_id = models.IntegerField()
    code = models.CharField(max_length=128)

    def __str__(self):
        return self.pk

    @staticmethod
    def get_membership_notification_or_None(user_id, community_id, code):
        try:
            return MemberNotification.objects.get(user_id=user_id, community_id=community_id, code=code)
        except:
            return None

    @staticmethod
    def create_instance(notification_body):
        instance = MemberNotification()
        instance.user_id = notification_body['user_id']
        instance.community_id = notification_body['community_id']
        instance.code = notification_body['code']
        instance.save()

        return instance

    def save(self, *args, **kwargs):

        super(MemberNotification, self).save(*args, **kwargs)
