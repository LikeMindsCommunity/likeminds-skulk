from payments.plans.plans_manager import PlansManager
from payments.models import Plans

class PlansImpl(PlansManager):

    def create_plan(self, req_body: dict) -> dict:
        
        if not req_body:
            return {'error_message': 'No plan details received'}
        
        plan_instance = Plans.create_instance(req_body)

        if not plan_instance:
            return {'error_message': 'Error while plan creation'}

        return plan_instance
        