from django.conf import settings

PENDING_MEMBER = 3
ADMIN = 1
COMMUNITY_API = "{}/api/community/fetch".format(settings.CORE_SERVICE_URL)
MEMBER_STATE_API = "{}/api/members_state".format(settings.CORE_SERVICE_URL)
COMMUNITY_QUESTIONS_API = "{}/api/questions".format(settings.CORE_SERVICE_URL)
REMOVE_MEMBER_API = "{}/api/community_membership/remove_member".format(settings.CORE_SERVICE_URL)
EDIT_COMMUNITY_API = "{}/api/v1/edit_community".format(settings.CORE_SERVICE_URL)
ALL_MEMBERS_API = "{}/api/v1/all_members".format(settings.CORE_SERVICE_URL)
ALL_MEMBERS_DETAILS_API = "{}/api/community_member/fetch_members_detail".format(settings.CORE_SERVICE_URL)
FETCH_OTL_URL = "{}/api/community/fetch_otl_url".format(settings.CORE_SERVICE_URL)
RENEW_MEMBER_API = "{}/api/community_membership/renew_member".format(settings.CORE_SERVICE_URL)
CHATROOM_EVENT_ATTEND = "{}/api/chatroom/event/attend".format(settings.CORE_SERVICE_URL)
CHATROOM_EVENT_UPDATE = "{}/api/chatroom/event/update".format(settings.CORE_SERVICE_URL)
CHATROOM_FETCH = "{}/api/chatroom/fetch".format(settings.CORE_SERVICE_URL)
USER_FETCH = "{}/api/user".format(settings.CORE_SERVICE_URL)
SEND_EMAIL = "{}/api/external_service_apis/send_email".format(settings.CORE_SERVICE_URL)
SEND_WHATSAPP_MESSAGES = "{}/api/external_service_apis/send_wa_bulk_messages".format(settings.CORE_SERVICE_URL)
SEND_NOTIFICATIONS = "{}/api/external_service_apis/send_notifications".format(settings.CORE_SERVICE_URL)
COMMUNITY_ADMINS_API = "{}/api/admins".format(settings.CORE_SERVICE_URL)
CREATE_COHORT_API = "{}/api/cohort/create".format(settings.CORE_SERVICE_URL)
UPDATE_COHORT_API = "{}/api/cohort/update".format(settings.CORE_SERVICE_URL)
