from ..subscription.subscription_manager import SubscriptionManager
from ..subscription.constants import subscription_plan_choices
from ..subscription.serializers import PlanSerializer
from ..utility.plan_utilities import PlanUtilities

from ..models import SubscriptionPlan


class SubscriptionImpl(SubscriptionManager):

    @staticmethod
    def _create_new_plan_object(plan_body: dict) -> dict:

        if 'name' not in plan_body or not plan_body['name']:
            plan_body['name'] = ""
        
        if plan_body['duration_name'] in subscription_plan_choices:
            plan_body['duration_in_months'] = subscription_plan_choices[plan_body['duration_name']]
        
        if 'trials' not in plan_body or not plan_body['trials']:
            plan_body['trials'] = 0
        
        return plan_body

    @staticmethod
    def _update_existing_plan_object(plan_body: dict, plan_instance: dict) -> dict:

        if plan_instance.name != plan_body['name']:
            plan_instance.name = plan_body['name']

        if plan_instance.cost != plan_body['cost']:
            plan_instance.cost = plan_body['cost']

        if plan_instance.cm_emails != plan_body['cm_emails']:
            plan_instance.cm_emails = plan_body['cm_emails']

        if plan_instance.buddy_emails != plan_body['buddy_emails']:
            plan_instance.buddy_emails = plan_body['buddy_emails']

        return plan_instance

    @staticmethod
    def _generate_response_from_plan(plan_instance: dict) -> dict:

        if not plan_instance.plan_id:
            return {'error_message': 'issue with created plan object'}

        return {'url': PlanUtilities.generate_plan_url(plan_instance.plan_id)}

    def create_plan(self, plan_body: dict) -> dict:

        if 'plan_id' not in plan_body or not plan_body['plan_id']:
            
            plan_instance_body = self._create_new_plan_object(plan_body)
            plan_instance = SubscriptionPlan.create_instance(plan_instance_body)

            if not plan_instance:
                return {'error_message': 'error creating plan'}

            response = self._generate_response_from_plan(plan_instance)

            return response

        else:

            plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=plan_body['plan_id'])

            if not plan_instance:
                return {'error_message': 'invalid plan_id'}

            plan_updated_instance = self._update_existing_plan_object(plan_body, plan_instance)
            plan_updated_instance.save()

            response = self._generate_response_from_plan(plan_updated_instance)

            return response

    @staticmethod
    def _fetch_plans(community_id):
        return SubscriptionPlan.objects.filter(community_id=community_id).order_by('created_at')

    @staticmethod
    def _serialize_plans(plans):
        return PlanSerializer(plans)

    def fetch_plan(self, community_id: str) -> dict:

        plans = self._fetch_plans(community_id)

        if len(plans) == 0:
            return {'error_message': 'no plans exist with provided community_id'}

        return self._serialize_plans(plans)

    @staticmethod
    def _delete_plan_instance(plan_instance: dict) -> dict:

        if not plan_instance.is_deleted:
            plan_instance.is_deleted = True

        return plan_instance

    def delete_plan(self, plan_id: str) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=plan_id)

        if not plan_instance:
            return {'error_message': 'invalid plan_id'}

        plan_deleted_instance = self._delete_plan_instance(plan_instance)
        plan_deleted_instance.save()

        return {'success': True}

    def create_order(self, order_body: dict) -> dict:
        pass

    def verify_order(self, payment_body: dict) -> dict:
        pass

    def create_transaction(self, transaction_body: dict) -> dict:
        pass

    def update_transaction(self, payment_id: str) -> dict:
        pass

    def create_subscription(self, payment_id: str) -> dict:
        pass
