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
    },
    "lifetime": {
        "unique": True,
        "title": "Lifetime",
        "subtitle": "lifetime"
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

EVENT_PAYMENT_LINK = "%s/event_pay?event_plan_id=%s&chatroom_id=%s&community_id=%s"

FIRST_MEMBERSHIP_PLAN_CM_MAIL_SUBJECT = "Hi {}! You have successfully created a membership plan"
FIRST_MEMBERSHIP_PLAN_CM_MAIL_BODY = """
<p>Hi {}!</p>
<p>Congratulations on creating your first membership plan with LikeMinds. You have taken the first step to build a paid 
membership community. Start inviting members to the community by using the link below or head over to the community 
to view the details.</p> 
"""
FIRST_MEMBERSHIP_PLAN_CM_MAIL_AFTER_CODE = """
<p>If you are facing any issues or want some help, we would love to help you thought the process. Just reply to this 
email and we will be right there</p>  
<p>Regards</p>
<p>Team LikeMinds</p>"""
FIRST_MEMBERSHIP_PLAN_CM_REPLY_EMAIL = "LikeMinds<hi@likeminds.community>"
FIRST_MEMBERSHIP_PLAN_CM_MAIL_BUTTON_TEXT = "INVITE MEMBERS"

