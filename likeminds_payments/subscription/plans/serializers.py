from ..utility.plan_utilities import PlanUtilities


def PlanSerializer(plans) -> list:

    output = []

    for plan in plans:
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
