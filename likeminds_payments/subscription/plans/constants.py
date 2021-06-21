from django.conf import settings

SUBSCRIPTION_PLAN_CHOICES = {
    "monthly": 1,
    "quarterly": 3,
    "half_yearly": 6,
    "yearly": 12,
    "lifetime": 999
}
PLAN_BASE_URL = settings.URL
PLAN_IMAGES = {
    "monthly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a772ddb19c5_Price%20Icon%2001.svg",
    "quarterly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a251adb19c6_Price%20Icon%2002.svg",
    "half_yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
    "yearly": "",
    "lifetime": ""
}

