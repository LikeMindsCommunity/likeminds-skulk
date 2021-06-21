from ..plans.models import SubscriptionPlan
from ..plans.serializers import PlanSerializer


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
