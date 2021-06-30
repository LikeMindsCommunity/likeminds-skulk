from ..utility.time_utilities import TimeUtilities
from ..plans.serializers import PlanSerializer
from ..plans.models import SubscriptionPlan

from .constants import *


def getMembershipState(subscription_object: dict) -> int:

    current_time = TimeUtilities.current_time_in_milliseconds()

    if current_time > subscription_object['valid_till']:
        if current_time > subscription_object['valid_till_grace_period']:
            return STATUS_EXPIRED
        return STATUS_GRACE_PERIOD

    if current_time > subscription_object['renewal_due']:
        return STATUS_RENEWAL_DUE

    return STATUS_ACTIVE


def SubscriptionSerializer(subscriptions) -> list:

    output = []

    for subscription in subscriptions:
        subscription_object = {
            'id': subscription.id,
            'user_id': subscription.user_id,
            'community_id': subscription.community_id,
            'date_subscribed': subscription.date_subscribed,
            'valid_till': subscription.valid_till,
            'date_unsubscribed': subscription.date_unsubscribed,
            'type': subscription.type,
            'renewal_due': subscription.renewal_due,
            'grace_period': 0,
            'valid_till_grace_period': subscription.valid_till,
            'membership_state': 0,
            'plan': None
        }

        if subscription.transaction is not None:
            subscription_plan = SubscriptionPlan.get_plan_or_None(plan_id=subscription.plan_id)
            if subscription_plan is not None:
                serialized_plans = PlanSerializer([subscription_plan])
                subscription_object['plan'] = serialized_plans[0]
            subscription_object['grace_period'] = subscription.transaction.grace_period
            subscription_object['valid_till_grace_period'] = TimeUtilities.add_milliseconds_in_epoch_time(
                subscription.valid_till, subscription.transaction.grace_period)

        subscription_object['membership_state'] = getMembershipState(subscription_object)

        output.append(subscription_object)

    return output


def SubscriptionListSerializer(member_subscriptions) -> dict:

    output = {}

    for key in member_subscriptions.keys():

        output[key] = SubscriptionSerializer(member_subscriptions[key])

    return output
