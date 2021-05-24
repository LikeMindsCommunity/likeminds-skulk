subscription_plan_choices = {
    "monthly": 1,
    "quarterly": 3,
    "half_yearly": 6,
    "yearly": 12,
    "lifetime": 999
}

plan_base_url = "https://payment.likeminds.community"
likeminds_logo_url = "https://uploads-ssl.webflow.com/605033ad58253a624fdb1964/6055d9b3d5d4c689c60acac7_Favicon%20256X256.jpg"
order_text = "Order Payment"
company_name = "Collabmates Pvt. Ltd."
community_api = "https://www.likeminds.community/api/community"

valid_webhook_events = [
    "refund.processed",
    "payment.captured",
    "payment.failed",
]
