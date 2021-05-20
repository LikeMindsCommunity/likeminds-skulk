from ..utility.plan_utilities import PlanUtilities


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
                'trials': plan.trials,
                'url': PlanUtilities.generate_plan_url(plan.plan_id)
            }

            output.append(plan_object)

    return output
