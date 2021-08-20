from .constants import *
from .models import SubscriptionPlan
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities


class PlanViewHelper:

    @staticmethod
    def create_plan_body_validator(plan_body, user_id) -> dict:

        if not plan_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        if 'plan_id' not in plan_body or not plan_body['plan_id']:

            if 'community_id' not in plan_body or not plan_body['community_id']:
                return {'error_message': 'send community_id'}

            if 'duration_name' not in plan_body or not plan_body['duration_name']:
                return {'error_message': 'send duration_name of plan'}

            if plan_body['duration_name'] not in SUBSCRIPTION_PLAN_CHOICES:
                return {'error_message': 'invalid duration_name'}

            if 'cost' not in plan_body or not plan_body['cost']:
                return {'error_message': 'send cost of plan'}

            if 'cm_emails' not in plan_body or not plan_body['cm_emails']:
                return {'error_message': 'send cm_emails'}

        else:

            if 'community_id' in plan_body:
                return {'error_message': 'community_id cannot be updated'}

            if 'duration_name' in plan_body:
                return {'error_message': 'duration_name cannot be updated'}

        if 'referral_free_days' in plan_body:
            if not isinstance(plan_body['referral_free_days'], int) or int(plan_body['referral_free_days']) < 0:
                return {'error_message': 'invalid referral_free_days value'}

        return plan_body

    @staticmethod
    def _new_plan_validator(plan_body) -> dict:

        plans = SubscriptionPlan.objects.filter(duration_name=plan_body['duration_name'],
                                                community_id=plan_body['community_id'])

        if len(plans) != 0:
            return {'error_message': 'plan already exist with provided duration_name, update existing one'}

        return plan_body

    @staticmethod
    def _create_new_plan_instance(plan_body) -> dict:

        if 'cost' in plan_body or plan_body['cost']:
            plan_body['cost'] = NumberUtilities.convert_to_paisa_or_none(plan_body['cost'])

        if 'strike_cost' not in plan_body or not plan_body['strike_cost']:
            plan_body['strike_cost'] = None
        else:
            plan_body['strike_cost'] = NumberUtilities.convert_to_paisa_or_none(plan_body['strike_cost'])

        if 'cost_usd' not in plan_body or not plan_body['cost_usd']:
            plan_body['cost_usd'] = None
        else:
            plan_body['cost_usd'] = NumberUtilities.convert_to_paisa_or_none(plan_body['cost_usd'])

        if 'strike_cost_usd' not in plan_body or not plan_body['strike_cost_usd']:
            plan_body['strike_cost_usd'] = None
        else:
            plan_body['strike_cost_usd'] = NumberUtilities.convert_to_paisa_or_none(plan_body['strike_cost_usd'])

        if 'name' not in plan_body or not plan_body['name']:
            plan_body['name'] = ""

        if plan_body['duration_name'] in SUBSCRIPTION_PLAN_CHOICES:
            plan_body['duration_in_months'] = SUBSCRIPTION_PLAN_CHOICES[plan_body['duration_name']]

        if 'description' not in plan_body or not plan_body['description']:
            plan_body['description'] = ''

        if 'referral_free_days' not in plan_body or not plan_body['referral_free_days']:
            plan_body['referral_free_days'] = 0

        if 'image' not in plan_body or not plan_body['image']:
            plan_body['image'] = PLAN_IMAGES[plan_body['duration_name']]

        try:
            plan_instance = SubscriptionPlan.create_instance(plan_body)
        except:
            return {'error_message': 'error_while creating new plan'}

        return {'plan_instance': plan_instance}

    @staticmethod
    def _update_existing_plan_instance(plan_body, plan_instance) -> dict:

        if 'name' in plan_body and plan_instance.name != plan_body['name']:
            plan_instance.name = plan_body['name']

        if 'cost' in plan_body:
            plan_instance.cost = NumberUtilities.convert_to_paisa_or_none(plan_body['cost'])

        if 'strike_cost' in plan_body:
            plan_instance.strike_cost = NumberUtilities.convert_to_paisa_or_none(plan_body['strike_cost'])

        if 'cost_usd' in plan_body:
            plan_instance.cost_usd = NumberUtilities.convert_to_paisa_or_none(plan_body['cost_usd'])

        if 'strike_cost_usd' in plan_body:
            plan_instance.strike_cost_usd = NumberUtilities.convert_to_paisa_or_none(plan_body['strike_cost_usd'])

        if 'cm_emails' in plan_body and plan_instance.cm_emails != plan_body['cm_emails']:
            plan_instance.cm_emails = plan_body['cm_emails']

        if 'buddy_emails' in plan_body and plan_instance.buddy_emails != plan_body['buddy_emails']:
            plan_instance.buddy_emails = plan_body['buddy_emails']

        if 'description' in plan_body and plan_instance.description != plan_body['description']:
            plan_instance.description = plan_body['description']

        if 'referral_free_days' in plan_body and plan_instance.referral_free_days != plan_body['referral_free_days']:
            plan_instance.referral_free_days = plan_body['referral_free_days']

        if 'image' in plan_body and plan_instance.image != plan_body['image']:
            plan_instance.image = plan_body['image']

        try:
            plan_instance.save()
        except:
            return {'error_message': 'error while editing existing plan'}

        return {'plan_instance': plan_instance}

    @staticmethod
    def create_plan_instance_helper(plan_body, user_id) -> dict:

        if 'plan_id' not in plan_body or not plan_body['plan_id']:

            has_permission_check = CoreServiceUtilities.has_permission(plan_body['community_id'], user_id)

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            # plan_validator = PlanViewHelper._new_plan_validator(plan_body)
            #
            # if 'error_message' in plan_validator:
            #     return {'error_message': plan_validator['error_message']}

            plan_instance = PlanViewHelper._create_new_plan_instance(plan_body)

            if 'error_message' in plan_instance:
                return {'error_message': plan_instance['error_message']}

            return plan_instance

        else:

            plan_instance = SubscriptionPlan.get_plan_or_None(plan_body['plan_id'])

            if plan_instance is None:
                return {'error_message': 'invalid plan_id'}

            has_permission_check = CoreServiceUtilities.has_permission(plan_instance.community_id, user_id)

            if 'error_message' in has_permission_check:
                return {'error_message': has_permission_check['error_message']}

            if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
                return {'error_message': 'You are not the Owner/CM of the community'}

            updated_plan_instance = PlanViewHelper._update_existing_plan_instance(plan_body, plan_instance)

            if 'error_message' in updated_plan_instance:
                return {'error_message': plan_instance['error_message']}

            return updated_plan_instance

    @staticmethod
    def get_plan_filter_params(request) -> dict:

        query_params = {}

        if request.GET.get('community_id'):
            query_params['community_id'] = request.GET.get('community_id')

        else:
            return {'error_message': 'send community_id in query params'}

        return query_params

    @staticmethod
    def delete_plan_body_validator(request_body, user_id) -> dict:

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in request_body or not request_body['plan_id']:
            return {'error_message': 'send plan_id'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        return request_body

    @staticmethod
    def delete_plan_instance_helper(request_body, user_id) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=request_body['plan_id'])

        if not plan_instance:
            return {'error_message': 'invalid plan_id'}

        has_permission_check = CoreServiceUtilities.has_permission(plan_instance.community_id, user_id)

        if 'error_message' in has_permission_check:
            return {'error_message': has_permission_check['error_message']}

        if 'has_permission' in has_permission_check and has_permission_check['has_permission'] is False:
            return {'error_message': 'You are not the Owner/CM of the community'}

        plan_instance.is_deleted = True

        try:
            plan_instance.save()
        except:
            return {'error_message': 'error while editing existing plan'}

        return {'plan_instance': plan_instance}

    @staticmethod
    def validate_request_body_for_create_event_plan_view(req_body):

        if not req_body:
            return {'success': False, 'error_message': "Invalid request"}

        chatroom_id = req_body.get('chatroom_id')

        if not chatroom_id:
            return {'success': False, 'error_message': "In-valid chatroom id"}

        community_id = req_body.get('community_id')

        if not community_id:
            return {'success': False, 'error_message': "In-valid community id"}

        return {}

    @staticmethod
    def validate_request_body_for_update_event_plan_view(req_body):

        if not req_body:
            return {'success': False, 'error_message': "Invalid request"}

        event_plan_id = req_body.get('event_plan_id')

        if not event_plan_id:
            return {'success': False, 'error_message': "In-valid event plan id"}

        return {}
