FREE_SUBSCRIPTION = 'free'
LIFETIME_PAYMENT = 'lifetime'
ONETIME_PAYMENT = 'onetime'
LIFETIME_VALID_TILL = 1924972199000
ONETIME_DESCRIPTION = 'onetime payment'
LIFETIME_DESCRIPTION = 'lifetime payment'
RENEWAL_DESCRIPTION = 'renewal payment'
FREE_DESCRIPTION = 'free subscription'
DASHBOARD = 'dashboard'
MIGRATION = 'migration'
MANUAL_PAYMENT_PAGE = 'manual_payment_page'
PAID = 'paid'
ONLINE_MODE = 'online'
FREE_MODE = 'free'
STATUS_ACTIVE = 0
STATUS_EXPIRED = 1
STATUS_GRACE_PERIOD = 2
STATUS_RENEWAL_DUE = 3
DAYS_FOR_FREE_USERS = 7
VALID_MONTH_PLAN_NAMES = ['monthly', 'quarterly', 'half_yearly', 'yearly', 'lifetime']
DAYS = 'days'
WEEKLY = 'weekly'
VALID_SHEET_COLUMNS = ['plan_id', 'member_email', 'member_phone (with country code)',
                       'start_date (dd/mm/yyyy)', 'community_id', 'payment_page_url', 'amount']
OTL_SUBJECT = 'OTL Migration Data'
REPORT_SUBJECT = 'Members Report File'
OTL_EMAIL = 'himanshu@likeminds.community'
MEMBERSHIP_STATES = {
    0: 'Active',
    1: 'Expired',
    2: 'Grace Period',
    3: 'Renewal Due'
}
SUBSCRIPTION_COHORT_NAME = 'Subscription Plan - {}'
SUBSCRIPTION_EXPIRED_COHORT_NAME = 'Subscription Expired Plan'

PAYMENT_SUCCESS_MEMBERSHIP_WHATSAPP_TEMPLATE_NAME = "payment_successful_new_v3"
PAYMENT_SUCCESS_MEMBERSHIP_WHATSAPP_BROADCAST_NAME = "cash_membership_successful_api"
PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_CM_SUBJECT = "New Member Joined"
PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_MEMBER_SUBJECT = "Community Join Link - {}"
PAYMENT_SUCCESS_MEMBERSHIP_RENEW_EMAIL_TO_CM_SUBJECT = "Membership Renewed - {}"
