from .constants import *
from .models import SubscriptionPlan


class PlanViewHelper:

    @staticmethod
    def create_plan_body_validator(plan_body) -> dict:

        if not plan_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in plan_body or not plan_body['plan_id']:

            if 'community_id' not in plan_body or not plan_body['community_id']:
                return {'error_message': 'send community_id'}

            if 'duration_name' not in plan_body or not plan_body['duration_name']:
                return {'error_message': 'send duration_name of plan'}

            if plan_body['duration_name'] not in SUBSCRIPTION_PLAN_CHOICES:
                return {'error_message': 'invalid duration_name'}

        else:

            if 'community_id' in plan_body:
                return {'error_message': 'community_id cannot be updated'}

            if 'duration_name' in plan_body:
                return {'error_message': 'duration_name cannot be updated'}

        if 'cost' not in plan_body or not plan_body['cost']:
            return {'error_message': 'send cost of plan'}

        if plan_body['cost'] == 0:
            return {'error_message': 'cost of plan cannot be zero'}

        if 'cm_emails' not in plan_body or not plan_body['cm_emails']:
            return {'error_message': 'send cm_emails'}

        if 'buddy_emails' not in plan_body or not plan_body['buddy_emails']:
            return {'error_message': 'send buddy_emails'}

        if 'referral_free_days' in plan_body:
            if not isinstance(plan_body['referral_free_days'], int) or int(plan_body['referral_free_days']) < 0:
                return {'error_message': 'invalid referral_free_days value'}

        return plan_body

    @staticmethod
    def create_plan_instance_helper(plan_body) -> dict:

        if 'plan_id' not in plan_body or not plan_body['plan_id']:

            if 'name' not in plan_body or not plan_body['name']:
                plan_body['name'] = ""

            if plan_body['duration_name'] in SUBSCRIPTION_PLAN_CHOICES:
                plan_body['duration_in_months'] = SUBSCRIPTION_PLAN_CHOICES[plan_body['duration_name']]

            if 'description' not in plan_body or not plan_body['description']:
                plan_body['description'] = ''

            if 'referral_free_days' not in plan_body or not plan_body['referral_free_days']:
                plan_body['referral_free_days'] = 0

            if 'image' not in plan_body or not plan_body['image']:
                plan_body['image'] = ''
                # TODO
                # assigning default values according to length of plan

            try:
                plan_instance = SubscriptionPlan.create_instance(plan_body)
            except:
                return {'error_message': 'error_while creating new plan'}

            return {'plan_instance': plan_instance}

        else:

            plan_instance = SubscriptionPlan.get_plan_or_None(plan_body['plan_id'])

            if plan_instance is None:
                return {'error_message': 'invalid plan_id'}

            if plan_instance.name != plan_body['name']:
                plan_instance.name = plan_body['name']

            if plan_instance.cost != plan_body['cost']:
                plan_instance.cost = plan_body['cost']

            if plan_instance.cm_emails != plan_body['cm_emails']:
                plan_instance.cm_emails = plan_body['cm_emails']

            if plan_instance.buddy_emails != plan_body['buddy_emails']:
                plan_instance.buddy_emails = plan_body['buddy_emails']

            if plan_instance.description != plan_body['description']:
                plan_instance.description = plan_body['description']

            if plan_instance.referral_free_days != plan_body['referral_free_days']:
                plan_instance.referral_free_days = plan_body['referral_free_days']

            if plan_instance.image != plan_body['image']:
                plan_instance.image = plan_body['image']

            try:
                plan_instance.save()
            except:
                return {'error_message': 'error while editing existing plan'}

            return {'plan_instance': plan_instance}

    @staticmethod
    def get_plan_filter_params(request):

        query_params = {}

        if request.GET.get('community_id'):
            query_params['community_id'] = request.GET.get('community_id')

        else:
            return {'error_message': 'send community_id in query params'}

        return query_params

    @staticmethod
    def delete_plan_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in request_body or not request_body['plan_id']:
            return {'error_message': 'send plan_id'}

        return request_body
