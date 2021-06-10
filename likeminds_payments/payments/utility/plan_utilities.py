from ..subscription.constants import plan_base_url


class PlanUtilities:

    @staticmethod
    def generate_plan_url(plan_id) -> str:
        return '{url}/{plan_id}'.format(url=plan_base_url, plan_id=plan_id)
