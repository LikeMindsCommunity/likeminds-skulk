NOTIFY_PERIOD = 3
VALID_WEBHOOK_EVENTS = [
    "refund.processed",
    "payment.captured",
    "payment.failed",
]
TRANSACTIONS_PAGE_SIZE = 50
CHATROOM_LINK = "%s/collabcard/%s"

TRANSACTION_DOWNLOAD_ALL_CSV_COLUMN_ORDERING_PAYMENT_PAGE_ID = ["Payment ID", "Name", "Phone", "Email ID", "Amount",
                                                                "Created On", "Status"]

TRANSACTION_DOWNLOAD_ALL_PAYMENT_PAGE_CSV_COLUMN_MAPPER = {
    "payment_id": "Payment ID",
    "payment_name": "Name",
    "payment_phone": "Phone",
    "payment_email": "Email ID",
    "amount": "Amount",
    "created_at": "Created On",
    "status": "Status"
}

PAYMENTS_STATUS_MAPPER = {
    'FAILED': 'Failed',
    'CAPTURED': 'Received',
    'REFUND': 'Refunded'
}

PAYMENTS_STATUS_FILTER = {
    'FAILED': 'failed',
    'CAPTURED': 'captured',
    'REFUNDED': 'refund'
}

TRANSACTION_DOWNLOAD_ALL_PAYMENT_PAGE_FILE_NAME = "Payment_page_report_{}_{}.csv"

TRANSACTION_DOWNLOAD_ALL_PAYMENT_PAGEREPORT_TO_CM_BODY = {
    "subject": "Payment page report"
}

DAY_OF_MONTH_FOR_REVENUE_CALCULATION = 1
CASH_PAYMENT_STATUS = ['migration', 'manual_payment_page']

EVENT_PAYMENT_SUCCESS_WHATSAPP_TEMPLATE_NAME = "event_payment_successful_v2"
EVENT_PAYMENT_SUCCESS_WHATSAPP_BROADCAST_NAME = "event_payment_successful"
