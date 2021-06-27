from ..plans.constants import PLAN_BASE_URL


class PlanUtilities:

    @staticmethod
    def generate_plan_url(plan_id) -> str:
        return '{url}/?plan_id={plan_id}'.format(url=PLAN_BASE_URL, plan_id=plan_id)
