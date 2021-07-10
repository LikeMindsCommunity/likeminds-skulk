from django.conf import settings

LIKEMINDS_LOGO_URL = \
    "https://uploads-ssl.webflow.com/605033ad58253a624fdb1964/6055d9b3d5d4c689c60acac7_Favicon%20256X256.jpg"
ORDER_TEXT = "Order Payment"
COMPANY_NAME = "Collabmates Pvt. Ltd."
COMMUNITY_API = "{}/api/community/fetch".format(settings.CORE_SERVICE_URL)
MEMBER_STATE_API = "{}/api/members_state".format(settings.CORE_SERVICE_URL)
COMMUNITY_QUESTIONS_API = "{}/api/questions".format(settings.CORE_SERVICE_URL)
REMOVE_MEMBER_API = "{}/api/community_membership/remove_member".format(settings.CORE_SERVICE_URL)
EDIT_COMMUNITY_API = "{}/api/v1/edit_community".format(settings.CORE_SERVICE_URL)
ALL_MEMBERS_API = "{}/api/v1/all_members".format(settings.CORE_SERVICE_URL)
INDIA_CODE = "IN"
USD_CURRENCY = "USD"
