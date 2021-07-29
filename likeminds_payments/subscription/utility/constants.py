from django.conf import settings

PENDING_MEMBER = 3
ADMIN = 1
COMMUNITY_API = "{}/api/community/fetch".format(settings.CORE_SERVICE_URL)
MEMBER_STATE_API = "{}/api/members_state".format(settings.CORE_SERVICE_URL)
COMMUNITY_QUESTIONS_API = "{}/api/questions".format(settings.CORE_SERVICE_URL)
REMOVE_MEMBER_API = "{}/api/community_membership/remove_member".format(settings.CORE_SERVICE_URL)
EDIT_COMMUNITY_API = "{}/api/v1/edit_community".format(settings.CORE_SERVICE_URL)
ALL_MEMBERS_API = "{}/api/v1/all_members".format(settings.CORE_SERVICE_URL)
FETCH_OTL_URL = "{}/api/community/fetch_otl_url".format(settings.CORE_SERVICE_URL)
RENEW_MEMBER_API = "{}/api/community_membership/renew_member".format(settings.CORE_SERVICE_URL)
