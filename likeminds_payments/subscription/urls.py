from django.urls import path
from .plans.plan_view_impl import *
from .orders.order_view_impl import *
from .transactions.transaction_view_impl import *
from .subscriptions.subscription_view_impl import *
from .subscription_histories.subscription_history_view_impl import *
from .payment_page.payment_page_view_impl import *
from .leads.lead_view_impl import *

app_name = "subscription"

urlpatterns = [
    path('create_plan', CreatePlanView.as_view(), name="create-plan"),
    path('fetch_plan', FetchPlanView.as_view(), name="fetch-plan"),
    path('delete_plan', DeletePlanView.as_view(), name="delete-plan"),
    path('fetch_country_code', FetchCountryCodeView.as_view(), name="fetch-country-code"),
    path('create_order', CreateOrderView.as_view(), name="create-order"),
    path('verify_order', VerifyOrderView.as_view(), name="verify-order"),
    path('create_transaction', CreateTransactionView.as_view(), name="create-transaction"),
    path('fetch_transactions', FetchTransactionsView.as_view(), name="fetch-transactions"),
    path('refund_transaction', RefundTransactionView.as_view(), name="refund-transaction"),
    path('create_subscription', CreateSubscriptionView.as_view(), name="create-subscription"),
    path('transactions/download_all', DownloadAllTransactionView.as_view(), name="download-all-transaction"),
    path('start', StartSubscriptionView.as_view(), name="start-subscription"),
    path('fetch', FetchSubscriptionView.as_view(), name="fetch-subscription"),
    path('cancel', CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path('fetch_history', FetchSubscriptionHistoryView.as_view(), name='fetch-subscription-history'),
    path('fetch_community_meta', FetchCommunityMetaView.as_view(), name='fetch-community-meta'),
    path('convert_to_paid', ConvertToPaidView.as_view(), name='convert-to-paid'),
    path('external_migrate', ExternalMigrationView.as_view(), name='external_migration'),
    path('external_renew_migrate', ExternalRenewMigrateView.as_view(), name='external_renew_migrate'),
    path('payment_page/add_cash', PaymentPageAddCashView.as_view(), name='payment_page_add_cash'),
    path('members_report', MembersReportView.as_view(), name='get-members-report'),
    path('create_event_plan', CreateEventPlanView.as_view(), name='create_event_plan'),
    path('fetch_event_plan', FetchEventPlanView.as_view(), name='create_event_plan'),
    path('create_event_order', CreateEventOrderView.as_view(), name='create_event_order'),
    path('valid_event_transaction', ValidateEventTransactionView.as_view(), name='valid_event_transaction'),
    path('send_facebook_event', SendEventView.as_view(), name='send-facebook-event'),
    path('valid_event_payment_id', ValidateEventPaymentView.as_view(), name='valid_event_payment_id'),
    path('update_payment_id', UpdatePaymentView.as_view(), name='update_payment_id'),
    path('update_event_plan', UpdateEventPlanView.as_view(), name='update_event_plan'),
    path('create_community_event_order', CreateCommunityEventOrderView.as_view(), name='create_community_event_order'),
    path('payment_page/create', CreatePaymentPageView.as_view(), name='create_payment_page'),
    path('payment_page/update', UpdatePaymentPageView.as_view(), name='update_payment_page'),
    path('payment_page/fetch_all', FetchAllPaymentPageView.as_view(), name='fetch_all_payment_page'),
    path('payment_page/download_all', DownloadAllPaymentPageView.as_view(), name='download_all_payment_page'),
    path('payment_page/fetch', FetchPaymentPageView.as_view(), name='fetch_payment_page'),
    path('payment_page/fetch_contact_us', FetchContactUsView.as_view(), name='fetch_contact_us'),
    path('create_payment_page_order', CreatePaymentPageOrderView.as_view(), name='create_payment_page_order')
]
