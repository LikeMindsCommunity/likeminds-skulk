from django.db.models import Sum, Count
from django.conf import settings

from ..payment_page.payment_page_manager import PaymentPageManager
from .models import PaymentPageMeta
from ..payment_page.payment_page_view_helper import PaymentPageViewHelper
from ..utility.model_utilities import ModelUtilities
from ..utility.csv_utilities import CsvUtilities
from ..utility.time_utilities import TimeUtilities
from ..payment_page.constants import *
from ..payment_page.serializers import PaymentPageMetaSerializer

from ..transactions.models import Transaction
from ..utility.core_service_utilities import CoreServiceUtilities


class PaymentPageImpl(PaymentPageManager):

    def __init__(self, user_id: str = None, community_id: str = None, payment_page_instance: PaymentPageMeta = None):
        self.user_id = user_id
        self.community_id = community_id
        self.payment_page_instance = payment_page_instance

    def get_user_id(self) -> str:
        return self.user_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_payment_page_instance(self) -> PaymentPageMeta:
        return self.payment_page_instance

    def set_user_id(self, user_id) -> None:
        self.user_id = user_id

    def set_community_id(self, community_id) -> None:
        self.community_id = community_id

    def set_payment_page_instance(self, payment_page_instance) -> None:
        self.payment_page_instance = payment_page_instance

    @staticmethod
    def fetch_transaction_data_for_payment_page_ids(payment_page_ids):

        transaction_filter = ModelUtilities.get_model_filter(Transaction, {'plan_id__in': payment_page_ids}). \
            values('plan_id').annotate(total_amount=Sum('amount'), total_payments=Count('plan_id'))

        transaction_data = {}

        for transaction_object in transaction_filter:
            transaction_data[transaction_object['plan_id']] = {
                'total_amount': transaction_object['total_amount'],
                'total_payments': transaction_object['total_payments'],
                'payment_page_url': ''.join([settings.WEB_URL if settings.WEB_URL else '',
                                             '/payment_page?payment_page_id=',
                                             transaction_object['plan_id']]),
            }

        return transaction_data

    def fetch_all_payment_page(self, req_body) -> dict:

        has_permission_check = PaymentPageViewHelper.check_cm_permission(self.get_community_id(), self.get_user_id())

        if 'error_message' in has_permission_check:
            return {'success': False, 'error_message': has_permission_check['error_message']}

        payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                              {"community_id": self.get_community_id()})

        total_payment_pages_count = len(payment_page_filter)

        if not payment_page_filter:
            return {'success': True, 'payment_pages': []}

        sort_type = 'created_at' if not req_body.get('sort_type') else req_body.get('sort_type')
        sort_order = PAYMENT_PAGE_DESCENDING_ORDER if not req_body.get('sort_order') else req_body.get('sort_order')
        sort_order_sign = '-' if sort_order == PAYMENT_PAGE_DESCENDING_ORDER else ''

        payment_page_filter = payment_page_filter.order_by(sort_order_sign + sort_type)

        if req_body.get('page'):
            payment_page_filter_paginated = ModelUtilities.paginate_queryset(payment_page_filter, int(req_body.get(
                'page')), 20)

        else:
            payment_page_filter_paginated = payment_page_filter

        payment_page_ids = list(payment_page_filter_paginated.values_list('payment_page_id', flat=True))

        transaction_data = self.fetch_transaction_data_for_payment_page_ids(payment_page_ids)

        payment_page_meta_serialized_object = PaymentPageMetaSerializer(payment_page_filter_paginated, many=True).data

        payment_pages_data = []

        for payment_page_object in payment_page_meta_serialized_object:
            payment_page_data = dict(payment_page_object)

            if payment_page_data['payment_page_id'] in transaction_data:
                payment_page_data = {**payment_page_data, **transaction_data[payment_page_data['payment_page_id']]}

            else:
                payment_page_data = {**payment_page_data,
                                     **{'payment_page_url': ''.join([settings.WEB_URL if settings.WEB_URL else '',
                                                                     '/payment_page?payment_page_id=',
                                                                     payment_page_data['payment_page_id']])}}

            payment_pages_data.append(payment_page_data)

        return {'success': True, 'payment_pages': payment_pages_data, 'total_payment_pages': total_payment_pages_count}

    def fetch_payment_page(self, payment_page_id) -> dict:

        payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                              {"payment_page_id": payment_page_id})

        if not payment_page_filter:
            return {'success': False, 'error_message': 'invalid payment_page_id'}

        self.set_payment_page_instance(payment_page_filter[0])

        transaction_data = self.fetch_transaction_data_for_payment_page_ids([payment_page_id])

        payment_page_object = PaymentPageMetaSerializer(self.get_payment_page_instance(), many=False).data

        if payment_page_object['payment_page_id'] in transaction_data:
            payment_page_object = {**payment_page_object, **transaction_data[payment_page_object['payment_page_id']]}

        else:
            payment_page_object = {**payment_page_object,
                                   **{'payment_page_url': ''.join([settings.WEB_URL if settings.WEB_URL else '',
                                                                   '/payment_page?payment_page_id=',
                                                                   payment_page_object['payment_page_id']])}}

        # Get Community Data
        community_object = CoreServiceUtilities.get_community_data(self.get_payment_page_instance().community_id)

        return {'success': True, 'payment_page': payment_page_object, 'community': community_object}

    def fetch_contact_us(self) -> dict:

        user_email_phone_object = PaymentPageViewHelper.get_first_verified_email_and_phone(user_id=self.get_user_id())

        if 'error_message' in user_email_phone_object:
            return {'success': False, 'error_message': user_email_phone_object['error_message']}

        return {'success': True, 'contact_us': user_email_phone_object}

    def download_all_payment_page(self) -> dict:

        payment_page_fetch = self.fetch_all_payment_page({})

        if payment_page_fetch.get('success') and payment_page_fetch.get('payment_pages', []):
            payment_pages_data = payment_page_fetch.get('payment_pages', [])

            payment_pages_df = CsvUtilities().object_list_to_dataframe(
                payment_pages_data, col_sequence=PAYMENT_PAGE_DOWNLOAD_ALL_CSV_COLUMN_ORDERING,
                col_map=PAYMENT_PAGE_DOWNLOAD_ALL_CSV_COLUMN_MAPPER)

            payment_pages_df['Status'] = payment_pages_df['Status'].apply(lambda x: 'Active' if x else 'Inactive')
            payment_pages_df['Created On'] = payment_pages_df['Created On'].apply(
                lambda x: TimeUtilities.convert_epoch_time_to_date_month_year(x) + "\n" +
                TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(x))

            CsvUtilities.pd_dataframe_to_csv(payment_pages_df, 'test.csv')

        return {}
