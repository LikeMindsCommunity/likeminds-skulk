from __future__ import absolute_import, unicode_literals

from celery import shared_task
from rest_framework import status as status_codes
from django.template.loader import get_template
from .subscription_manager import SubscriptionManager
from ..plans.plan_view_helper import PlanViewHelper
from ..transactions.models import Transaction
from .models import Subscription
from ..subscription_histories.models import SubscriptionHistory
from ..plans.models import SubscriptionPlan
from ..member_notifications.models import MemberNotification
from ..member_acquisition.models import MemberAcquisition
from .constants import *
from .serializers import SubscriptionSerializer, SubscriptionListSerializer

from ..utility.constants import *
from ..utility.states import TransactionType
from ..utility.time_utilities import TimeUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.async_tasks import (payment_success_membership_join_communication,
                                   cash_payment_renewal_communication,
                                   payment_page_member_payment_success_email,
                                   payment_page_cm_payment_success_email)
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper
from ..external_services.logging.logging_wrapper import LoggingWrapper
from ..plans.constants import *
from ..transactions.constants import *
from ..member_notifications.constants import *
from ..external_services.email.email_wrapper import MailWrapper
from ..external_services.s3.s3_wrapper import S3Wrapper
from scripts.external_community_migration import generate_transactions

import time
import uuid
import razorpay
import analytics
import pandas as pd
from io import StringIO

error_logger = LoggingWrapper.get_instance()
info_logger = LoggingWrapper.get_instance()


class SubscriptionImpl(SubscriptionManager):

    payment_id = None
    user_id = None
    community_id = None
    subscription_type = None
    member_id = None

    def __init__(self, payment_id: str = None, user_id: str = None, community_id: str = None,
                 subscription_type: str = None, member_id: str = None):
        self.payment_id = payment_id
        self.user_id = user_id
        self.community_id = community_id
        self.subscription_type = subscription_type
        self.member_id = member_id

    def get_payment_id(self) -> str:
        return self.payment_id

    def get_user_id(self) -> str:
        return self.user_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_subscription_type(self) -> str:
        return self.subscription_type

    def get_member_id(self) -> str:
        return self.member_id

    @staticmethod
    def _remove_member_notifications(user_id: str, community_id: str):

        MemberNotification.objects.filter(user_id=user_id, community_id=community_id).delete()

    @staticmethod
    def _check_if_transaction_is_used(payment_id: str) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=payment_id)

        if transaction_instance is None:
            return {'error_message': 'no transaction exists for given payment_id'}

        if Subscription.objects.filter(transaction=transaction_instance).exists():
            return {'abort_execution': 'special case'}

        if SubscriptionHistory.objects.filter(transaction=transaction_instance).exists():
            return {'abort_execution': 'special case'}

        return {'transaction': transaction_instance}

    @staticmethod
    def _get_subscription_valid_till(start_time_epoch: int, subscription_plan_instance: SubscriptionPlan):

        valid_till = start_time_epoch

        if subscription_plan_instance.duration_name in VALID_MONTH_PLAN_NAMES:
            valid_till = TimeUtilities.add_months_in_epoch_time(start_time_epoch,
                                                                subscription_plan_instance.duration_in_months)

        if subscription_plan_instance.duration_name == WEEKLY:
            valid_till = TimeUtilities.add_weeks_in_epoch_time(start_time_epoch,
                                                               subscription_plan_instance.duration_in_months)

        if subscription_plan_instance.duration_name == DAYS:
            valid_till = TimeUtilities.add_days_in_epoch_time(start_time_epoch,
                                                              subscription_plan_instance.duration_in_months)

        return valid_till

    @staticmethod
    def _generate_data_for_new_subscription_against_transaction(transaction_instance: Transaction,
                                                                subscription_plan_instance: SubscriptionPlan,
                                                                user_id: int) -> dict:

        data = {
            "subscription_data": {
                "user_id": transaction_instance.user_id,
                "community_id": subscription_plan_instance.community_id,
                "plan_id": subscription_plan_instance.plan_id,
                "date_subscribed": transaction_instance.created_at,
                "valid_till": SubscriptionImpl._get_subscription_valid_till(transaction_instance.created_at,
                                                                            subscription_plan_instance),
                "type": "onetime",
                "transaction": transaction_instance,
            }
        }

        if subscription_plan_instance.duration_in_months == SUBSCRIPTION_PLAN_CHOICES["lifetime"]:
            data["subscription_data"]["type"] = LIFETIME_PAYMENT
            data["subscription_data"]["valid_till"] = LIFETIME_VALID_TILL

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": transaction_instance.created_at,
            "end_date": data["subscription_data"]["valid_till"],
            "description": ONETIME_DESCRIPTION,
            "transaction": transaction_instance,
            "type": "paid",
            "user_id": user_id,
            "community_id": subscription_plan_instance.community_id
        }

        if subscription_plan_instance.duration_in_months == SUBSCRIPTION_PLAN_CHOICES["lifetime"]:
            data["subscription_history_data"]["description"] = LIFETIME_DESCRIPTION

        return data

    @staticmethod
    def _generate_data_for_existing_subscription_against_transaction(subscription_instance: Subscription,
                                                                     subscription_plan_instance: SubscriptionPlan,
                                                                     transaction_instance: Transaction) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        data = {
            "subscription_data": {
                "type": "onetime",
                "valid_till": 0,
                "transaction": transaction_instance,
                "plan_id": subscription_plan_instance.plan_id
            }
        }

        existing_valid_till = subscription_instance.valid_till

        if existing_valid_till >= current_time:
            data["subscription_data"]["valid_till"] = SubscriptionImpl._get_subscription_valid_till(
                existing_valid_till, subscription_plan_instance)
        else:
            data["subscription_data"]["valid_till"] = SubscriptionImpl._get_subscription_valid_till(
                current_time, subscription_plan_instance)

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": RENEWAL_DESCRIPTION,
            "transaction": transaction_instance,
            "type": "paid",
            "user_id": subscription_instance.user_id,
            "community_id": subscription_instance.community_id
        }

        if existing_valid_till >= current_time:
            data["subscription_history_data"]["start_date"] = existing_valid_till

        return data

    @staticmethod
    def _generate_data_for_existing_subscription_against_referral(subscription_instance: Subscription,
                                                                  subscription_plan_instance: SubscriptionPlan,
                                                                  transaction_instance: Transaction) -> dict:
        current_time = TimeUtilities.current_time_in_milliseconds()
        existing_valid_till = subscription_instance.valid_till

        data = {
            "subscription_data": {
                "valid_till": TimeUtilities.add_days_in_epoch_time(
                    existing_valid_till, subscription_plan_instance.referral_free_days)
            }
        }

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": current_time,
            "end_date": data["subscription_data"]["valid_till"],
            "description": 'renewal payment',
            "transaction": transaction_instance,
            "type": "referral",
            "user_id": subscription_instance.user_id,
            "community_id": subscription_instance.community_id
        }

        if existing_valid_till >= current_time:
            data["subscription_history_data"]["start_date"] = existing_valid_till

        return data

    @staticmethod
    def _generate_first_transaction(transaction_instance: Transaction, plan_instance: SubscriptionPlan, user_id: int):

        if transaction_instance.user_id is None:
            transaction_instance.user_id = user_id
            transaction_instance.save()

            subscription_instance = Subscription.get_subscription_or_None(user_id, plan_instance.community_id)

            if subscription_instance is not None:
                renewal = SubscriptionImpl._generate_renewal_transaction(transaction_instance, plan_instance, user_id)
                return renewal

            data = SubscriptionImpl._generate_data_for_new_subscription_against_transaction(
                transaction_instance, plan_instance, user_id)

            subscription_instance = Subscription.create_instance(data['subscription_data'])
            subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

            if not subscription_instance:
                return {'error_message': 'error creating subscription'}

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            if transaction_instance.shared_by is not None:
                referrer_subscription_instance = Subscription.get_subscription_or_None(
                    transaction_instance.shared_by, plan_instance.community_id
                )

                if referrer_subscription_instance is None or referrer_subscription_instance.type != ONETIME_PAYMENT:
                    return {'success': True}

                referrer_data = SubscriptionImpl._generate_data_for_existing_subscription_against_referral(
                    referrer_subscription_instance, plan_instance, transaction_instance)

                referrer_subscription_instance.valid_till = referrer_data["subscription_data"]["valid_till"]
                referrer_subscription_instance.renewal_due = referrer_data["subscription_data"]["renewal_due"]
                referrer_subscription_instance.save()

                referrer_subscription_history_instance = SubscriptionHistory.create_instance(
                    referrer_data['subscription_history_data'])

                if not referrer_subscription_history_instance:
                    return {'error_message': 'error creating subscription history for referrer user'}

            return {'success': True}

        return {'error_message': 'Payment ID already used'}

    @staticmethod
    def _generate_renewal_transaction(transaction_instance: Transaction, plan_instance: SubscriptionPlan, user_id):

        if transaction_instance.user_id is None:
            return {'error_message': "user ID doesn't exist for renewal transaction"}

        if transaction_instance.user_id != user_id:
            return {'error_message': 'Invalid user ID'}

        subscription_instance = Subscription.get_subscription_or_None(
            transaction_instance.user_id, plan_instance.community_id
        )

        if not subscription_instance:
            return {'error_message': 'no subscription exists for given user in given community'}

        if subscription_instance.type == LIFETIME_PAYMENT:
            return {'error_message': 'cannot renew a lifetime subscription'}

        data = SubscriptionImpl._generate_data_for_existing_subscription_against_transaction(
            subscription_instance, plan_instance, transaction_instance)

        subscription_instance.type = data["subscription_data"]["type"]
        subscription_instance.valid_till = data["subscription_data"]["valid_till"]
        subscription_instance.renewal_due = data["subscription_data"]["renewal_due"]
        subscription_instance.transaction = data["subscription_data"]["transaction"]
        subscription_instance.plan_id = data["subscription_data"]["plan_id"]
        subscription_instance.is_removed = False
        subscription_instance.save()

        SubscriptionImpl._remove_member_notifications(subscription_instance.user_id, subscription_instance.community_id)

        subscription_history_instance = SubscriptionHistory.create_instance(data['subscription_history_data'])

        if not subscription_history_instance:
            return {'error_message': 'error creating subscription history'}

        return {'success': True}

    @staticmethod
    def _generate_subscription_against_transaction(transaction_instance: Transaction, user_id: str) -> dict:

        user_id = NumberUtilities.get_integer_from_string(user_id)
        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'no plan exist for this transaction, contact your cm.'}

        if not transaction_instance.renew:

            community_data = CoreServiceUtilities.get_community_data(plan_instance.community_id)

            if community_data.get('error_message'):
                return {'error_message': community_data['error_message'], 'status_code': community_data['status_code']}

            transaction = SubscriptionImpl._generate_first_transaction(transaction_instance, plan_instance, user_id)

            community_dict = community_data.get('community')

            if community_dict and community_dict.get('auto_approval'):
                cohort_response = PlanViewHelper.add_member_to_subscription_cohort(
                    plan_id=transaction_instance.plan_id,
                    user_id=user_id,
                    community_id=plan_instance.community_id)

                if 'error_message' in cohort_response:
                    return {'error_message': cohort_response['error_message'],  'status_code': cohort_response['status_code']}

            return transaction

        if transaction_instance.renew:

            transaction = SubscriptionImpl._generate_renewal_transaction(transaction_instance, plan_instance, user_id)

            cohort_response = PlanViewHelper.add_member_to_subscription_cohort(
                plan_id=transaction_instance.plan_id,
                user_id=user_id,
                community_id=plan_instance.community_id)

            if 'error_message' in cohort_response:
                return {'error_message': cohort_response['error_message'],  'status_code': cohort_response['status_code']}

            return transaction

    @staticmethod
    def _generate_data_for_free_subscription(user_id: int, community_id: int, date_subscribed: int) -> dict:

        current_time = TimeUtilities.current_time_in_milliseconds()
        date_subscribed = current_time if date_subscribed == 0 else date_subscribed

        data = {
            "subscription_data": {
                "user_id": user_id,
                "community_id": community_id,
                "plan_id": None,
                "date_subscribed": date_subscribed,
                "valid_till": LIFETIME_VALID_TILL,
                "date_unsubscribed": None,
                "type": "free",
                "transaction": None
            }
        }

        data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
            data["subscription_data"]["valid_till"], NOTIFY_PERIOD)

        data["subscription_history_data"] = {
            "start_date": date_subscribed,
            "end_date": data["subscription_data"]["valid_till"],
            "description": FREE_DESCRIPTION,
            "transaction": None,
            "type": "free",
            "user_id": user_id,
            "community_id": community_id
        }

        return data

    @staticmethod
    def _generate_free_subscription(user_id: str, community_id: str):

        user_id = NumberUtilities.get_integer_from_string(user_id)
        community_id = NumberUtilities.get_integer_from_string(community_id)

        subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

        if subscription_instance is None:
            data = SubscriptionImpl._generate_data_for_free_subscription(user_id, community_id, 0)

            subscription_instance = Subscription.create_instance(data['subscription_data'])
            subscription_history_instance = SubscriptionHistory.create_instance(
                data['subscription_history_data'])

            if not subscription_instance:
                return {'error_message': 'error creating subscription'}

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        else:
            data = SubscriptionImpl._generate_data_for_free_subscription(user_id,
                                                                         community_id,
                                                                         subscription_instance.date_subscribed)

            subscription_instance.plan_id = data['subscription_data']['plan_id']
            subscription_instance.date_subscribed = data['subscription_data']['date_subscribed']
            subscription_instance.valid_till = data['subscription_data']['valid_till']
            subscription_instance.type = data['subscription_data']['type']
            subscription_instance.renewal_due = data['subscription_data']['renewal_due']
            subscription_instance.transaction = data['subscription_data']['transaction']
            subscription_instance.is_removed = False
            subscription_instance.save()

            SubscriptionImpl._remove_member_notifications(subscription_instance.user_id,
                                                          subscription_instance.community_id)

            subscription_history_instance = SubscriptionHistory.create_instance(
                data['subscription_history_data'])

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

    @staticmethod
    def _add_free_days_to_subscription(user_id: str, community_id: str, valid_till: str, n_days: str):

        user_id = NumberUtilities.get_integer_from_string(user_id)
        community_id = NumberUtilities.get_integer_from_string(community_id)
        valid_till = NumberUtilities.get_integer_from_string(valid_till)
        n_days = NumberUtilities.get_integer_from_string(n_days)
        subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

        if subscription_instance is not None:

            existing_valid_till = subscription_instance.valid_till

            if valid_till is not None and valid_till > existing_valid_till and n_days is None:
                subscription_instance.valid_till = valid_till

            if valid_till is None and n_days is not None:
                subscription_instance.valid_till = TimeUtilities.add_days_in_epoch_time(
                    subscription_instance.valid_till, n_days)

            subscription_instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(
                subscription_instance.valid_till, NOTIFY_PERIOD)

            subscription_instance.save()

            SubscriptionImpl._remove_member_notifications(subscription_instance.user_id,
                                                          subscription_instance.community_id)

            subscription_history_data = {
                "start_date": existing_valid_till,
                "end_date": subscription_instance.valid_till,
                "description": 'free limited subscription',
                "transaction": None,
                "type": "free",
                "user_id": user_id,
                "community_id": community_id
            }

            subscription_history_instance = SubscriptionHistory.create_instance(subscription_history_data)

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        return {'error_message': 'invalid user_id and community_id pair'}

    @staticmethod
    def _send_subscription_event(subscription_history_instance: SubscriptionHistory,
                                 subscription_instance: Subscription) -> None:

        if None not in [subscription_instance, subscription_history_instance]:

            event = EVENTS['SUBSCRIPTION_STARTED']['event']

            event_data = {
                'user_id': subscription_history_instance.user_id,
                'community_id': subscription_history_instance.community_id,
                'community_name': '',
                'plan_name': '',
                'amount': 0,
                'end_date': TimeUtilities.convert_epoch_to_date(subscription_history_instance.end_date),
                'no_of_days': (subscription_history_instance.end_date -
                               subscription_history_instance.start_date) // TimeUtilities.MILLISECONDS_IN_A_DAY,
                'mode_of_payment': FREE_MODE,
                'type': subscription_instance.type
            }

            if subscription_instance.transaction is None:
                community_data = CoreServiceUtilities.get_community_data(subscription_instance.community_id)

                if 'error_message' not in community_data:
                    event_data['community_name'] = community_data['community']['name']
            else:
                event_data['community_name'] = subscription_instance.transaction.community_name
                event_data['plan_name'] = subscription_instance.transaction.plan_name
                event_data['amount'] = NumberUtilities.convert_to_rupee_or_none(
                    subscription_instance.transaction.amount)
                event_data['mode_of_payment'] = ONLINE_MODE
                if subscription_instance.transaction.renew:
                    event = EVENTS['SUBSCRIPTION_RENEWED']['event']

            analytics.track(subscription_history_instance.user_id, event, event_data)

    @staticmethod
    def _convert_to_paid_save_subscription_instance(subscription_instance, valid_till):

        subscription_instance.plan_id = None
        subscription_instance.valid_till = valid_till
        subscription_instance.type = FREE_SUBSCRIPTION
        subscription_instance.transaction = None
        subscription_instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(valid_till, NOTIFY_PERIOD)
        subscription_instance.save()

    @staticmethod
    def _convert_to_paid_create_subscription_history_dict(current_time, valid_till, user_id, community_id):

        return {
                "start_date": current_time,
                "end_date": valid_till,
                "description": FREE_DESCRIPTION,
                "transaction": None,
                "type": "free",
                "user_id": user_id,
                "community_id": community_id
            }

    @staticmethod
    def _convert_to_paid_existing_subscription(community_id, user_id):

        subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

        if subscription_instance is None:
            return {'error_message': 'Invalid user_id'}

        if (subscription_instance.type != FREE_SUBSCRIPTION or
                subscription_instance.valid_till != LIFETIME_VALID_TILL):
            return {'error_message': 'The user is not a free user'}

        if subscription_instance is not None:

            current_time = TimeUtilities.current_time_in_milliseconds()
            valid_till = TimeUtilities.add_days_in_epoch_time(current_time, DAYS_FOR_FREE_USERS)

            SubscriptionImpl._convert_to_paid_save_subscription_instance(subscription_instance, valid_till)

            subscription_history_data = SubscriptionImpl._convert_to_paid_create_subscription_history_dict(
                current_time, valid_till, user_id, community_id)

            subscription_history_instance = SubscriptionHistory.create_instance(subscription_history_data)

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        return {'error_message': 'Invalid user_id'}

    @staticmethod
    def _send_analytics_for_free_days_add(user_id, community_id, valid_till, n_days):

        community_data = CoreServiceUtilities.get_community_data(community_id)

        if 'community' in community_data:
            analytics_data = {
                'community_id': community_id,
                'community_name': community_data['community'].get('name')
            }

            if n_days is not None:
                analytics_data['days_added'] = n_days

            if valid_till is not None:
                analytics_data['date_till_added'] = TimeUtilities.convert_epoch_to_date(valid_till)

            analytics.track(user_id, 'Extra days added (Backend)', analytics_data)

    @staticmethod
    def _send_common_analytics(community_id, user_id, event_name):

        community_data = CoreServiceUtilities.get_community_data(community_id)

        if 'community' in community_data:
            analytics_data = {
                'community_id': community_id,
                'community_name': community_data['community'].get('name')
            }

            analytics.track(user_id, event_name, analytics_data)

    def create_subscription(self, n_days: str = None, valid_till: str = None, shared_by: str = None) -> dict:

        if self.get_payment_id() is not None:

            transaction_validation = self._check_if_transaction_is_used(self.get_payment_id())

            if 'error_message' in transaction_validation:
                return {'error_message': transaction_validation['error_message']}

            if 'abort_execution' in transaction_validation:
                return {'abort_execution': transaction_validation['abort_execution']}

            transaction_instance = transaction_validation['transaction']

            generate_subscription = self._generate_subscription_against_transaction(transaction_instance,
                                                                                    self.get_member_id())

            member_acquisition_instance = MemberAcquisition.get_member_acquisition_or_None(transaction_instance.id)

            if member_acquisition_instance is not None:
                member_acquisition_instance.user_id = self.get_member_id()
                member_acquisition_instance.save()

            if 'error_message' in generate_subscription:
                return {'error_message': generate_subscription['error_message']}

            plan_instance = SubscriptionPlan.get_plan_or_None(transaction_instance.plan_id)
            subscription_instance = Subscription.get_subscription_or_None(
                self.get_member_id(), plan_instance.community_id)
            subscription_history_instance = SubscriptionHistory.get_latest_subscription_history_or_None(
                self.get_member_id(), plan_instance.community_id)

            self._send_subscription_event(subscription_history_instance, subscription_instance)

            return {'success': True}

        elif self.get_community_id() is not None and self.get_subscription_type() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check:
                if has_permission_check['has_permission'] is False and shared_by is None:
                    return {'error_message': 'You are not the Owner/CM of the community'}

                if self.get_subscription_type() == DASHBOARD:

                    add_free_days = self._add_free_days_to_subscription(self.get_user_id(),
                                                                        self.get_community_id(),
                                                                        valid_till, n_days)

                    if 'error_message' in add_free_days:
                        return {'error_message': add_free_days['error_message']}

                    self._send_analytics_for_free_days_add(self.get_user_id(),
                                                           self.get_community_id(),
                                                           valid_till, n_days)

                    return {'success': True}

                if self.get_subscription_type() == PAID:

                    generate_free_limited_subscription = self._convert_to_paid_existing_subscription(
                        self.get_community_id(), self.get_user_id())

                    if 'error_message' in generate_free_limited_subscription:
                        return {'error_message': generate_free_limited_subscription['error_message']}

                    self._send_common_analytics(self.get_community_id(),
                                                self.get_user_id(),
                                                'Converted to paid (Backend)')

                    return {'success': True}

                if self.get_subscription_type() == FREE_SUBSCRIPTION:

                    if shared_by is None:

                        generate_free_subscription = self._generate_free_subscription(self.get_user_id(),
                                                                                      self.get_community_id())

                        if 'error_message' in generate_free_subscription:
                            return {'error_message': generate_free_subscription['error_message']}

                        subscription_instance = Subscription.get_subscription_or_None(
                            self.get_user_id(), self.get_community_id())
                        subscription_history_instance = SubscriptionHistory.get_latest_subscription_history_or_None(
                            self.get_user_id(), self.get_community_id())

                        self._send_subscription_event(subscription_history_instance, subscription_instance)

                        self._send_common_analytics(self.get_community_id(),
                                                    self.get_user_id(),
                                                    'Convert to free (Backend)')

                        return {'success': True}

                    has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), shared_by)

                    if 'error_message' in has_permission_check:
                        return {'error_message': has_permission_check['error_message']}

                    if 'has_permission' in has_permission_check:
                        if has_permission_check['has_permission'] is False:
                            return {'error_message': 'shared_by user is not the Owner/CM of the community'}

                        generate_free_subscription = self._generate_free_subscription(self.get_member_id(),
                                                                                      self.get_community_id())

                        if 'error_message' in generate_free_subscription:
                            return {'error_message': generate_free_subscription['error_message']}

                        subscription_instance = Subscription.get_subscription_or_None(
                            self.get_member_id(), self.get_community_id())
                        subscription_history_instance = SubscriptionHistory.get_latest_subscription_history_or_None(
                            self.get_member_id(), self.get_community_id())

                        self._send_subscription_event(subscription_history_instance, subscription_instance)

                        return {'success': True}

            return {'error_message': 'You are not Owner/CM of this community'}

    def start_subscription(self) -> dict:

        subscription_instance = Subscription.get_subscription_or_None(user_id=self.get_member_id(),
                                                                      community_id=self.get_community_id())

        if subscription_instance is None:
            return {'error_message': 'no subscription exists for provided user_id and community_id'}

        return {'success': True}

        # if subscription_instance.created_at == subscription_instance.updated_at:
        #     current_time = TimeUtilities.current_time_in_milliseconds()
        #
        #     difference = current_time - subscription_instance.date_subscribed
        #
        #     subscription_instance.date_subscribed = current_time
        #     subscription_instance.valid_till = TimeUtilities.add_milliseconds_in_epoch_time(
        #         subscription_instance.valid_till, difference)
        #     subscription_instance.save()
        #
        #     return {'success': True}
        #
        # return {'error_message': 'something went wrong'}

    @staticmethod
    def _fetch_subscriptions(user_id: str, community_id: str):
        if community_id is not None:
            return Subscription.objects.filter(user_id=user_id, community_id=community_id).order_by('created_at')
        return Subscription.objects.filter(user_id=user_id).order_by('created_at')

    @staticmethod
    def _serialize_subscriptions(subscriptions):
        return SubscriptionSerializer(subscriptions)

    @staticmethod
    def _serialize_subscriptions_list(subscriptions):
        return SubscriptionListSerializer(subscriptions)

    def fetch_subscription(self, member_ids: list = None) -> dict:

        if member_ids is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            member_subscriptions = {}

            for member_id in member_ids:
                member_subscriptions[member_id] = self._fetch_subscriptions(member_id, self.get_community_id())

            return {'subscriptions': self._serialize_subscriptions_list(member_subscriptions)}

        subscriptions = self._fetch_subscriptions(self.get_member_id(), self.get_community_id())

        if len(subscriptions) == 0:
            return {'error_message': 'no subscriptions exist with provided user_id'}

        return {'subscriptions': self._serialize_subscriptions(subscriptions)}

    def cancel_subscription(self) -> dict:

        if self.get_user_id() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            subscription_instance = Subscription.get_subscription_or_None(user_id=self.get_user_id(),
                                                                          community_id=self.get_community_id())

        else:

            is_pending_member = CoreServiceUtilities.is_pending_member(self.get_community_id(), self.get_member_id())

            if 'error_message' in is_pending_member:
                return {'error_message': is_pending_member['error_message']}

            if is_pending_member['is_pending_member'] is False:
                return {'error_message': 'Your are not a pending member'}

            subscription_instance = Subscription.get_subscription_or_None(self.get_member_id(), self.get_community_id())

        if subscription_instance is None:
            return {'error_message': 'no subscription exists for this user_id and community_id'}

        if subscription_instance.transaction is None:
            return {'error_message': 'no active payment associated with this user subscription to be refunded'}

        razorpay_client = RazorpayWrapper.get_instance()

        try:
            response = razorpay_client.payment.refund(subscription_instance.transaction.payment_id,
                                                      subscription_instance.transaction.amount)
        except razorpay.errors.BadRequestError as e:
            return {'error_message': e.__str__()}

        try:
            subscription_instance.delete()
        except:
            return {'error_message': 'something went wrong'}

        return response

    def fetch_community_meta(self) -> dict:

        transaction_instance = Transaction.get_transaction_or_None(payment_id=self.get_payment_id())

        if transaction_instance is None:
            return {'error_message': 'Incorrect payment ID'}

        if transaction_instance.user_id is not None:
            return {'error_message': 'Payment ID already used'}

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=transaction_instance.plan_id)

        if plan_instance is None:
            return {'error_message': 'cannot retrieve community_id'}

        return {'community_id': plan_instance.community_id}

    @staticmethod
    def _get_all_members(community_id, member_id):

        members = []
        page = 1
        done = False

        while not done:

            get_members = CoreServiceUtilities.get_all_members(community_id, member_id, page)

            if 'error_message' in get_members:
                done = True
                continue

            if len(get_members['members']) == 0:
                done = True

            members += get_members['members']

            page += 1

        return members

    @staticmethod
    def _get_all_members_detail(community_id, member_id):

        members = []
        page = 1
        done = False

        while not done:

            get_members = CoreServiceUtilities.get_all_members_details(community_id, member_id, page)

            if 'error_message' in get_members:
                done = True
                continue

            if len(get_members['members']) == 0:
                done = True

            members += get_members['members']

            page += 1

        return members

    @staticmethod
    def _generate_new_free_subscription(community_id, user_id, date_subscribed):

        subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

        if subscription_instance is None:

            subscription_data = {
                "user_id": user_id,
                "community_id": community_id,
                "plan_id": None,
                "date_subscribed": date_subscribed,
                "valid_till": TimeUtilities.add_days_in_epoch_time(date_subscribed, DAYS_FOR_FREE_USERS),
                "type": "free",
                "transaction": None,
            }

            subscription_data["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
                subscription_data["valid_till"], NOTIFY_PERIOD)

            subscription_history_data = {
                "start_date": date_subscribed,
                "end_date": subscription_data["valid_till"],
                "description": FREE_DESCRIPTION,
                "transaction": None,
                "type": "free",
                "user_id": user_id,
                "community_id": community_id
            }

            subscription_instance = Subscription.create_instance(subscription_data)
            subscription_history_instance = SubscriptionHistory.create_instance(subscription_history_data)

            if not subscription_instance:
                return {'error_message': 'error creating subscription'}

            if not subscription_history_instance:
                return {'error_message': 'error creating subscription history'}

            return {'success': True}

        return {'error_message': 'subscription already exists'}

    def convert_to_paid(self, exempt_user_ids: list = None) -> dict:

        if self.get_member_id() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            community_update = CoreServiceUtilities.edit_community(self.get_community_id(), self.get_member_id())

            if 'error_message' in community_update:
                return {'error_message': community_update['error_message']}

            if 'success' in community_update and community_update['success']:

                members = self._get_all_members(self.get_community_id(), self.get_member_id())

                for member in members:

                    if member['state'] == ADMIN or member['id'] in exempt_user_ids:

                        generate_free_lifetime_subscription = self._generate_free_subscription(member['id'],
                                                                                               self.get_community_id())

                        if 'error_message' in generate_free_lifetime_subscription:
                            continue

                    else:

                        current_time = TimeUtilities.current_time_in_milliseconds()

                        generate_free_limited_subscription = self._generate_new_free_subscription(
                            self.get_community_id(), member['id'], current_time)

                        if 'error_message' in generate_free_limited_subscription:
                            continue

                return {'success': True}

        return {'error_message': 'something went wrong'}

    @staticmethod
    def _columns_validator(sheet_data: pd.DataFrame, columns: list) -> dict:

        for column in columns:
            if column not in sheet_data:
                return {'error_message': 'missing {} column in sheet'.format(column)}

        return {'sheet_data': sheet_data}

    @staticmethod
    @shared_task
    def _handle_migration(input_csv_url, emails):

        output_file_path = generate_transactions(input_file_path=input_csv_url)

        if 'error_message' in output_file_path:
            error_logger.error(output_file_path['error_message'])

        template = get_template("otl_mail.html").render(
            {"link": output_file_path['link']})

        to_emails = [OTL_EMAIL]

        if emails is not None:
            to_emails.extend(emails)

        status = MailWrapper.send_email(OTL_SUBJECT, template, to_emails)

        if not status:
            error_logger.error('error sending email')

    @staticmethod
    def _create_transaction_object(plan_id, amount, email, phone, type_id, community_id, payment_name: str = '',
                                   renew: bool = False, user_id: int = None):

        unique_id = uuid.uuid4()
        payment_id = 'mig_{}'.format(unique_id)
        method = MIGRATION

        if type_id == TransactionType.PAYMENT_PAGE:
            payment_id = 'ppc_{}'.format(unique_id)
            method = MANUAL_PAYMENT_PAGE

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id)

        if plan_instance is None:

            if type_id != TransactionType.PAYMENT_PAGE:
                return {'error_message': 'invalid plan_id', 'status': status_codes.HTTP_400_BAD_REQUEST}

            plan_name = ""
            plan_cost = amount

        else:
            plan_name = plan_instance.name
            plan_cost = plan_instance.cost

        community_data = CoreServiceUtilities.get_community_data(community_id)

        if 'error_message' in community_data:
            return {'error_message': community_data['error_message'],
                    'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

        transaction_data = {
            "plan_id": plan_id,
            "payment_id": payment_id,
            "community_name": community_data['community']['name'],
            "plan_name": plan_name,
            "plan_cost": plan_cost,
            "renew": renew,
            "amount": amount,
            "payment_email": email,
            "payment_phone": phone,
            "currency": 'INR',
            "is_international": False,
            "method": method,
            "status": 'captured',
            "error_description": "",
            "refund_amount": 0,
            "user_id": user_id,
            "payment_page_url": "",
            "grace_period": 0,
            "type": type_id,
            "type_id": community_id,
            "shared_by": None,
            "payment_name": payment_name
        }

        transaction_instance = Transaction.create_instance(transaction_data)

        return {'transaction': transaction_instance}

    def external_migration(self, request_body: dict) -> dict:

        if 'members_data_url' in request_body and request_body['members_data_url'] is not None:
            input_csv_url = request_body['members_data_url']

            if input_csv_url is None:
                return {'error_message': 'invalid members_data sheet link', 'status': status_codes.HTTP_400_BAD_REQUEST}

            df = pd.read_csv(input_csv_url)

            validated_data = self._columns_validator(df, VALID_SHEET_COLUMNS)

            if 'error_message' in validated_data:
                return {'error_message': validated_data['error_message'], 'status': status_codes.HTTP_400_BAD_REQUEST}

            self._handle_migration.delay(input_csv_url, request_body['emails'])

            return {'success': True,
                    'message': 'A mail will be sent to you with the details',
                    'status': status_codes.HTTP_200_OK}

        if not self.get_member_id():
            return {'error_message': 'send x-member-id in headers', 'status': status_codes.HTTP_400_BAD_REQUEST}

        has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message'],
                    'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community',
                    'status': status_codes.HTTP_401_UNAUTHORIZED}

        create_transaction = self._create_transaction_object(request_body['plan_id'],
                                                             request_body['amount'],
                                                             request_body['member_email'],
                                                             request_body['member_phone (with country code)'],
                                                             TransactionType.COMMUNITY_SUBSCRIPTION,
                                                             request_body['community_id'])

        if 'error_message' in create_transaction:
            return {'error_message': create_transaction['error_message'], 'status': create_transaction['status']}

        transaction = create_transaction['transaction']

        # send communications for member migration
        payment_success_membership_join_communication.delay(transaction.id)

        return {'success': True}

    def external_renew_migrate(self, request_body: dict) -> dict:

        if self.get_member_id() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message'],
                        'status': status_codes.HTTP_504_GATEWAY_TIMEOUT}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community',
                        'status': status_codes.HTTP_401_UNAUTHORIZED}

            user_details = CoreServiceUtilities.user_fetch({'member_id': request_body.get('user_id')})

            user_id = user_details['user']['id']
            user_emails = user_details['user']['emails']
            user_email = None
            if len(user_emails) > 0:
                user_email = user_emails[0]['email']
            user_phones = user_details['user']['mobiles']
            user_phone = None
            if len(user_phones) > 0:
                user_phone = '+{}{}'.format(user_phones[0]['country_code'], user_phones[0]['mobile_no'])

            create_transaction = self._create_transaction_object(request_body['plan_id'],
                                                                 request_body['amount'],
                                                                 user_email,
                                                                 user_phone,
                                                                 TransactionType.COMMUNITY_SUBSCRIPTION,
                                                                 request_body['community_id'],
                                                                 renew=True,
                                                                 user_id=user_id)

            if 'error_message' in create_transaction:
                return {'error_message': create_transaction['error_message'], 'status': create_transaction['status']}

            transaction = create_transaction['transaction']

            subscription_manager = SubscriptionImpl(payment_id=transaction.payment_id,
                                                    member_id=transaction.user_id)

            create_subscription = subscription_manager.create_subscription()

            if 'error_message' in create_subscription:
                return {'error_message': create_subscription['error_message'],
                        'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

            # send communications for member renewal migration
            cash_payment_renewal_communication.delay(transaction.id)

            return {'success': True}

        return {'error_message': 'send member-id in headers', 'status': status_codes.HTTP_400_BAD_REQUEST}

    def payment_page_add_cash(self, request_body: dict) -> dict:

        if self.get_member_id() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message'],
                        'status': status_codes.HTTP_500_INTERNAL_SERVER_ERROR}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community',
                        'status': status_codes.HTTP_401_UNAUTHORIZED}

            create_transaction = self._create_transaction_object(request_body['payment_page_id'],
                                                                 request_body['amount'],
                                                                 request_body['payment_email'],
                                                                 request_body['payment_phone'],
                                                                 TransactionType.PAYMENT_PAGE,
                                                                 request_body['community_id'],
                                                                 payment_name=request_body['payment_name'])

            if 'error_message' in create_transaction:
                return {'error_message': create_transaction['error_message'], 'status': create_transaction['status']}

            transaction = create_transaction['transaction']

            # Send Payment Page member success email and whatsapp
            payment_page_member_payment_success_email.delay(transaction.id)

            # Send Payment Page CM success email
            payment_page_cm_payment_success_email.delay(transaction.id)

            return {'success': True}

        return {'error_message': 'send member-id in headers', 'status': status_codes.HTTP_400_BAD_REQUEST}

    @staticmethod
    def _handle_report_data(members_detail, subscription_details, community_questions) -> dict:

        output_data = {
            'member_name': [],
            'member_phones': [],
            'member_emails': [],
            'join_date': [],
            'active_plan': [],
            'subscription_status': [],
            'subscription_valid_till': []
        }

        for question in community_questions:

            output_data[question['question_title']] = []

        for member_id in members_detail.keys():

            phones = ''
            for mobile in members_detail[member_id]['mobiles']:
                phones += '+{}-{}, '.format(mobile['country_code'], mobile['mobile_no'])
            phones = phones[:-2]

            emails = ''
            for email in members_detail[member_id]['emails']:
                emails += '{}, '.format(email['email'])
            emails = emails[:-2]

            join_date = time.strftime("%d %b %Y", time.localtime(members_detail[member_id]['created_at']))

            output_data['member_name'].append(members_detail[member_id]['name'])
            output_data['member_phones'].append(phones)
            output_data['member_emails'].append(emails)
            output_data['join_date'].append(join_date)

            for question in community_questions:
                match = next(filter(lambda entity: entity.get('question_id') == question['id'],
                                    members_detail[member_id]['question_answers']), None)

                if match is None:
                    output_data[question['question_title']].append('')
                else:
                    output_data[question['question_title']].append(match['value'])

            if len(subscription_details[member_id]) > 0:
                active_plan = subscription_details[member_id][0]['plan']
                if subscription_details[member_id][0]['type'] == FREE_SUBSCRIPTION:
                    active_plan = FREE_SUBSCRIPTION

                membership_state = MEMBERSHIP_STATES[subscription_details[member_id][0]['membership_state']]
                valid_till = time.strftime(
                    "%d %b %Y", time.localtime(subscription_details[member_id][0]['valid_till']/1000))

                output_data['active_plan'].append(active_plan)
                output_data['subscription_status'].append(membership_state)
                output_data['subscription_valid_till'].append(valid_till)
            else:
                output_data['active_plan'].append(None)
                output_data['subscription_status'].append(None)
                output_data['subscription_valid_till'].append(None)

        return output_data

    @staticmethod
    def _send_report(data, file_name):

        final_data = pd.DataFrame(data)
        csv_buffer = StringIO()
        final_data.to_csv(csv_buffer)

        file_path = 'utilities/report_files/{}'.format(file_name)
        bucket = settings.S3_BUCKETS.get('media_bucket').get('name')

        upload_status = S3Wrapper.upload_csv_file(file_path, bucket, csv_buffer, acl='public-read')

        if upload_status:
            return {'link': 'https://{}.s3.amazonaws.com/{}'.format(bucket, file_path)}

        return {'error_message': 'error while uploading csv file'}

    @staticmethod
    @shared_task
    def _fetch_all_member_data(community_id, member_id):

        cm_member_id = NumberUtilities.get_integer_from_string(member_id)
        members = SubscriptionImpl._get_all_members_detail(community_id, member_id)
        members_questions = SubscriptionImpl._get_all_members(community_id, member_id)
        community_questions = CoreServiceUtilities.get_community_questions(community_id, member_id)

        members_data = {}
        email = None

        for member in members:

            if email is None and member['id'] == cm_member_id:
                email = member['emails'][0]['email']

            members_data[member['id']] = member

        for member_questions in members_questions:

            members_data[member_questions['id']]['question_answers'] = member_questions.get('question_answers', [])

        subscription_manager = SubscriptionImpl(member_id=member_id, community_id=community_id)
        subscription_details = subscription_manager.fetch_subscription(list(members_data.keys()))

        report_data = SubscriptionImpl._handle_report_data(
            members_data, subscription_details['subscriptions'], community_questions['questions'])

        community_name = '-'.join(community_questions['community']['name'].split(' '))

        file_name = 'MemberDetails_{}_{}.csv'.format(
            community_name,
            time.strftime("%d-%b-%Y", time.localtime(time.time())))

        upload_status = SubscriptionImpl._send_report(report_data, file_name)

        if 'error_message' in upload_status:
            error_logger.error(upload_status['error_message'])

        template = get_template("member_report_mail.html").render(
            {"link": upload_status['link'], "community_name": community_name})

        to_emails = [email]

        status = MailWrapper.send_email(REPORT_SUBJECT, template, to_emails)

        if not status:
            error_logger.error('error sending email')

    def members_report(self) -> dict:

        if self.get_member_id() is not None:

            has_permission_check = CoreServiceUtilities.has_permission(self.get_community_id(), self.get_member_id())

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message'],
                        'status': status_codes.HTTP_401_UNAUTHORIZED}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community',
                        'status': status_codes.HTTP_401_UNAUTHORIZED}

            self._fetch_all_member_data.delay(self.get_community_id(), self.get_member_id())

            self._send_common_analytics(self.get_community_id(),
                                        self.get_user_id(),
                                        'Download member list (Backend)')

            return {'success': True}

        return {'error_message': 'something went wrong', 'status': status_codes.HTTP_400_BAD_REQUEST}
