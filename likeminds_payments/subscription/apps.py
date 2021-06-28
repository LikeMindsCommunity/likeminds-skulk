from django.apps import AppConfig
from django.conf import settings
import analytics


class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription'

    def ready(self):
        analytics.write_key = settings.SEGMENT_KEY
