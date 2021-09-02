from django.conf import settings

SUBSCRIPTION_PLAN_CHOICES = {
    "days": 1,
    "weekly": 1,
    "monthly": 1,
    "quarterly": 3,
    "half_yearly": 6,
    "yearly": 12,
    "lifetime": 999
}

SUBSCRIPTION_PLAN_NAMES = {
    "days": {
        "unique": False,
        "title": "Day/s",
        "subtitle": "day/s"
    },
    "weekly": {
        "unique": False,
        "title": "Week/s",
        "subtitle": "week/s"
    },
    "monthly": {
        "unique": False,
        "title": "Month/s",
        "subtitle": "month/s"
    },
    "quarterly": {
        "unique": True,
        "title": "Quarterly",
        "subtitle": "month/s"
    },
    "half_yearly": {
        "unique": True,
        "title": "Half Yearly",
        "subtitle": "month/s"
    },
    "yearly": {
        "unique": True,
        "title": "Yearly",
        "subtitle": "month/s"
    }
}
PLAN_BASE_URL = settings.URL
PLAN_IMAGES = {
    "monthly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a772ddb19c5_Price%20Icon%2001.svg",
    "quarterly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a251adb19c6_Price%20Icon%2002.svg",
    "half_yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
    "yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
    "lifetime": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
    "default": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg"
}

EVENT_PAYMENT_LINK = "%s/event_pay?event_plan_id=%s&chatroom_id=%s"
