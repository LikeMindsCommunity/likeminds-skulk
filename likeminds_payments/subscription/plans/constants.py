from django.conf import settings

SUBSCRIPTION_PLAN_CHOICES = {
    "monthly": 1,
    "quarterly": 3,
    "half_yearly": 6,
    "yearly": 12,
    "lifetime": 999
}
PLAN_BASE_URL = settings.URL
