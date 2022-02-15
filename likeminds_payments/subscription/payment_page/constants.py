PAYMENT_PAGE_AMOUNT_TYPE_FIXED = "fixed"
PAYMENT_PAGE_AMOUNT_TYPE_CUSTOMERS = "customers"

PAYMENT_PAGE_AMOUNT_TYPE_CHOICES = [PAYMENT_PAGE_AMOUNT_TYPE_FIXED, PAYMENT_PAGE_AMOUNT_TYPE_CUSTOMERS]

PAYMENT_PAGE_ASCENDING_ORDER = '0'
PAYMENT_PAGE_DESCENDING_ORDER = '1'

PAYMENT_PAGE_SORT_ORDER_CHOICES = [PAYMENT_PAGE_ASCENDING_ORDER, PAYMENT_PAGE_DESCENDING_ORDER]

PAYMENT_PAGE_DOWNLOAD_ALL_CSV_COLUMN_MAPPER = {
    "title": "Title",
    "total_amount": "Revenue",
    "total_payments": "Unit Sold",
    "payment_page_url": "URL",
    "created_at": "Created On",
    "is_active": "Status"
}

PAYMENT_PAGE_DOWNLOAD_ALL_CSV_COLUMN_ORDERING = ["Title", "Revenue", "Unit Sold", "URL", "Created On", "Status"]

PAYMENT_PAGE_ALL_REPORTS_DOWNLOAD_EMAIL_BODY = {
    "subject": "All payment pages report"
}

DOWNLOAD_ALL_PAYMENT_PAGE_FILE_NAME = "All_payment_pages_report_{}.csv"

PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_MEMBER_BODY = {
    "subject": "Payment successful for {}"
}

PAYMENT_PAGE_PAYMENT_FAILED_EMAIL_TO_MEMBER_BODY = {
    "subject": "Payment failed for {}"
}

PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_CM_BODY = {
    "subject": "Payment received for {}"
}

PAYMENT_PAGE_PAYMENT_SUCCESS_MEMBER_WHATSAPP_TEMPLATE_NAME = "payment_page_successfull_v1"
PAYMENT_PAGE_PAYMENT_SUCCESS_MEMBER_WHATSAPP_BROADCAST_NAME = "payment_page_success"
PAYMENT_PAGE_PAYMENT_FAILED_MEMBER_WHATSAPP_TEMPLATE_NAME = "failed_payment_member_v5"
PAYMENT_PAGE_PAYMENT_FAILED_MEMBER_WHATSAPP_BROADCAST_NAME = "payment_page_failed"

PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_TITLE = "New payment received"
PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_SUB_TITLE = "We have received a new payment of" \
                                                                 " {} {} for {}"
PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_ROUTE = "route://testing_route_push_notification"
PAYMENT_PAGE_SIZE = 25


class NotificationCategories:
    PAYMENT_PAGE_SUCCESSFUL = "Payment page successful"


class NotificationSubCategories:
    NEW_PAYMENT_ADDED = "New payment added"
