from ..utility.plan_utilities import PlanUtilities
from ..utility.time_utilities import TimeUtilities
from ..models import SubscriptionPlan


def PlanSerializer(plans, is_deleted=False) -> list:

    output = []

    for plan in plans:
        if plan.is_deleted == is_deleted:
            plan_object = {
                'plan_id': plan.plan_id,
                'community_id': plan.community_id,
                'name': plan.name,
                'duration_name': plan.duration_name,
                'cost': plan.cost,
                'duration_in_months': plan.duration_in_months,
                'cm_emails': plan.cm_emails,
                'buddy_emails': plan.buddy_emails,
                'description': plan.description,
                'referral_free_days': plan.referral_free_days,
                'image': plan.image,
                'url': PlanUtilities.generate_plan_url(plan.plan_id)
            }

            output.append(plan_object)

    return output


def _getMembershipState(subscription_object: dict) -> int:

    current_time = TimeUtilities.current_time_in_milliseconds()

    if current_time > subscription_object['valid_till']:
        if current_time > subscription_object['valid_till_grace_period']:
            return 1
        return 2

    if current_time > subscription_object['renewal_due']:
        return 3

    return 0


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
            'membership_state': 0
        }

        if subscription.transaction is not None:
            subscription_object['plan_id'] = subscription.transaction.plan_id
            subscription_object['grace_period'] = subscription.transaction.grace_period
            subscription_object['valid_till_grace_period'] = TimeUtilities.add_days_in_epoch_time(
                subscription.valid_till, subscription.transaction.grace_period)

        subscription_object['membership_state'] = _getMembershipState(subscription_object)

        output.append(subscription_object)

    return output


def SubscriptionHistorySerializer(subscription_history) -> list:

    output = []

    for entry in subscription_history:
        history_object = {
            'start_date': entry.start_date,
            'end_date': entry.end_date,
            'description': entry.description,
            'transaction': entry.transaction.id,
            'type': entry.type
        }

        if entry.type == 'free':
            history_object['duration_name'] = 'free'

        if entry.type == 'referral':
            history_object['duration_name'] = 'referral'

        if entry.transaction is not None:
            history_object['order_id'] = entry.transaction.payment_id

            subscription_plan = SubscriptionPlan.get_plan_or_None(plan_id=entry.transaction.plan_id)
            if subscription_plan is not None:
                history_object['duration_name'] = subscription_plan.duration_name
                serialized_plan = PlanSerializer([subscription_plan])
                history_object['plan'] = serialized_plan[0]

        output.append(history_object)

    return output
