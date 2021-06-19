from django.conf import settings

LIKEMINDS_LOGO_URL = \
    "https://uploads-ssl.webflow.com/605033ad58253a624fdb1964/6055d9b3d5d4c689c60acac7_Favicon%20256X256.jpg"
ORDER_TEXT = "Order Payment"
COMPANY_NAME = "Collabmates Pvt. Ltd."
COMMUNITY_API = "{}/api/community".format(settings.CORE_SERVICE_URL)
MEMBER_STATE_API = "{}/api/members_state".format(settings.CORE_SERVICE_URL)
COMMUNITY_QUESTIONS_API = "{}/api/questions".format(settings.CORE_SERVICE_URL)
