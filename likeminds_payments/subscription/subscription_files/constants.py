SUBSCRIPTION_PLAN_CHOICES = {
    "monthly": 1,
    "quarterly": 3,
    "half_yearly": 6,
    "yearly": 12,
    "lifetime": 999
}

PLAN_BASE_URL = "https://betapayment.likeminds.community"
LIKEMINDS_LOGO_URL = \
    "https://uploads-ssl.webflow.com/605033ad58253a624fdb1964/6055d9b3d5d4c689c60acac7_Favicon%20256X256.jpg"
ORDER_TEXT = "Order Payment"
COMPANY_NAME = "Collabmates Pvt. Ltd."
COMMUNITY_API = "https://www.likeminds.community/api/community"
MEMBER_STATE_API = "https://www.likeminds.community/api/members_state"
COMMUNITY_QUESTIONS_API = "https://www.likeminds.community/api/questions"
FREE_SUBSCRIPTION = 'free'
LIFETIME_VALID_TILL = 1924972199
NOTIFY_PERIOD = 3

VALID_WEBHOOK_EVENTS = [
    "refund.processed",
    "payment.captured",
    "payment.failed",
]
