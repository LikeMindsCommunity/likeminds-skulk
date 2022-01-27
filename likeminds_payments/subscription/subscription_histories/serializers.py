from ..plans.models import SubscriptionPlan
from ..plans.plan_helper import PlanHelper
from ..plans.serializers import PlanSerializer


def SubscriptionHistorySerializer(subscription_history) -> list:

    output = []

    for entry in subscription_history:
        history_object = {
            'start_date': entry.start_date,
            'end_date': entry.end_date,
            'description': entry.description,
            'transaction': None,
            'type': entry.type
        }

        if entry.type == 'free':
            history_object['duration_name'] = 'free'

        if entry.type == 'referral':
            history_object['duration_name'] = 'referral'

        if entry.transaction is not None:
            history_object['transaction'] = entry.transaction.id
            history_object['order_id'] = entry.transaction.payment_id

            subscription_plan = SubscriptionPlan.get_plan_or_None(plan_id=entry.transaction.plan_id)
            if subscription_plan is not None:
                history_object['duration_name'] = subscription_plan.duration_name
                plan_object = PlanSerializer(subscription_plan)
                plan_title_context = PlanHelper.get_plan_title_and_subtitle_for_plan(plan_object=plan_object,
                                                                                     plan_instance=subscription_plan)
                plan_object.update(plan_title_context)
                history_object['plan'] = plan_object

        output.append(history_object)

    return output
