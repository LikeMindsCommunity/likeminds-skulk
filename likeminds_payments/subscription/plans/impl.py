from ..plans.manager import PlanManager
from .models import SubscriptionPlan
from .serializers import PlanSerializer

from ..utility.plan_utilities import PlanUtilities


class PlanImpl(PlanManager):

    plan_id = None
    community_id = None
    plan_instance = None

    def __init__(self, plan_id: str = None, community_id: str = None, plan_instance: SubscriptionPlan = None):
        self.plan_id = plan_id
        self.community_id = community_id
        self.plan_instance = plan_instance

    def get_plan_id(self) -> str:
        return self.plan_id

    def get_community_id(self) -> str:
        return self.community_id

    def get_plan_instance(self) -> SubscriptionPlan:
        return self.plan_instance

    @staticmethod
    def _generate_response_from_plan(plan_instance: SubscriptionPlan) -> dict:

        if not plan_instance.plan_id:
            return {'error_message': 'issue with created plan object'}

        return {'url': PlanUtilities.generate_plan_url(plan_instance.plan_id)}

    def create_plan(self) -> dict:

        response = self._generate_response_from_plan(self.get_plan_instance())

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        return response

    @staticmethod
    def _fetch_plans(community_id: str):
        return SubscriptionPlan.objects.filter(community_id=community_id, is_deleted=False).order_by('created_at')

    @staticmethod
    def _serialize_plans(plans) -> list:
        return PlanSerializer(plans)

    def fetch_plan(self) -> dict:

        plans = self._fetch_plans(self.get_community_id())

        if len(plans) == 0:
            return {'error_message': 'no plans exist with provided community_id'}

        return {'plans': self._serialize_plans(plans)}

    @staticmethod
    def _delete_plan_instance(plan_instance: SubscriptionPlan) -> dict:

        if not plan_instance.is_deleted:
            plan_instance.is_deleted = True

            try:
                plan_instance.save()
            except:
                return {'error_message': 'error deleting plan'}

        return {'plan_instance': plan_instance}

    def delete_plan(self) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=self.get_plan_id())

        if plan_instance is None:
            return {'error_message': 'invalid plan_id'}

        plan_deleted_instance = self._delete_plan_instance(plan_instance)

        if 'error_message' in plan_deleted_instance:
            return {'error_message': plan_deleted_instance['error_message']}

        return {'success': True}
