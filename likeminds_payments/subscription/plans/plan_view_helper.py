from .constants import *
from .models import SubscriptionPlan, SubscriptionEventPlan, EventCohortPlan
from ..external_services.logging.logging_wrapper import LoggingWrapper
from ..subscriptions.constants import SUBSCRIPTION_COHORT_NAME, SUBSCRIPTION_EXPIRED_COHORT_NAME
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.response_utilities import ResponseUtilities
from ..utility.states import cohort_types, EventDiscountType
from ..utility.json_utilities import JsonUtilities

error_logger = LoggingWrapper.get_instance()


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

            if 'duration_in_months' in plan_body and not isinstance(plan_body['duration_in_months'], int):
                return {'error_message': 'duration_in_months must be integer'}

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

        if plan_body['duration_name'] in SUBSCRIPTION_PLAN_CHOICES and 'duration_in_months' not in plan_body:
            plan_body['duration_in_months'] = SUBSCRIPTION_PLAN_CHOICES[plan_body['duration_name']]

        if 'description' not in plan_body or not plan_body['description']:
            plan_body['description'] = ''

        if 'referral_free_days' not in plan_body or not plan_body['referral_free_days']:
            plan_body['referral_free_days'] = 0

        if 'image' not in plan_body or not plan_body['image']:
            if plan_body['duration_name'] in PLAN_IMAGES:
                plan_body['image'] = PLAN_IMAGES[plan_body['duration_name']]
            else:
                plan_body['image'] = PLAN_IMAGES['default']

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

        query_params = {
            'community_id': request.GET.get('community_id'),
            'plan_id': request.GET.get('plan_id')
        }

        if not query_params['community_id'] and not query_params['plan_id']:
            return ResponseUtilities.get_inner_error_context('send community_id or plan_id in query params')

        return query_params

    @staticmethod
    def get_event_plan_params(request) -> dict:

        query_params = {
            'chatroom_id__in': None,
            'event_plan_id': request.GET.get('event_plan_id', None)
        }

        if request.GET.get('chatroom_ids'):
            try:
                query_params['chatroom_id__in'] = JsonUtilities.load_json(request.GET.get('chatroom_ids', None))
            except:
                query_params['chatroom_id__in'] = None

        output = {}

        for param in query_params.keys():
            if query_params[param] is not None:
                output[param] = query_params[param]

        return output

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

    @staticmethod
    def create_subscription_plan_cohort(serialized_plan, user_id):
        cohort_info = {
            'member_id': user_id,
            'name': SUBSCRIPTION_COHORT_NAME.format(serialized_plan['plan_title']),
            'type': cohort_types.SUBSCRIPTION_PLAN,
            'type_id': serialized_plan['plan_id'],
            'community_id': serialized_plan['community_id'],
            'member_ids': []
        }

        response = CoreServiceUtilities.create_cohort(cohort_info)

        if response.get('error_message'):
            return {'error_message': response['error_message'], 'status_code': response['status_code']}

        return {}

    @staticmethod
    def create_subscription_expired_plan_cohort(community_id, user_id):
        cohort_info = {
            'member_id': user_id,
            'name': SUBSCRIPTION_EXPIRED_COHORT_NAME,
            'type': cohort_types.SUBSCRIPTION_EXPIRED_PLAN,
            'type_id': None,
            'community_id': community_id,
            'member_ids': []
        }

        response = CoreServiceUtilities.create_cohort(cohort_info)

        if response.get('error_message'):
            return {'error_message': response['error_message']}

        return {}

    @staticmethod
    def add_member_to_subscription_cohort(plan_id, user_id, community_id):

        cohort_info = {
            'member_id': user_id,
            'type': cohort_types.SUBSCRIPTION_PLAN,
            'type_id': plan_id,
            'community_id': community_id,
            'member_ids': [int(user_id)]
        }

        response = CoreServiceUtilities.update_cohort(cohort_info)

        if response.get('error_message'):
            return {'error_message': response['error_message'], 'status_code': response['status_code']}

        return {}

    @staticmethod
    def add_member_to_subscription_expired_cohort(user_id, community_id):

        cohort_info = {
            'member_id': user_id,
            'type': cohort_types.SUBSCRIPTION_EXPIRED_PLAN,
            'community_id': community_id,
            'member_ids': [int(user_id)]
        }

        response = CoreServiceUtilities.update_cohort(cohort_info)

        if response.get('error_message'):
            return {'error_message': response['error_message'], 'status_code': response['status_code']}

        return {}

    @staticmethod
    def calculate_event_cohort_plan_discount(cohort_plan):
        discount_type = cohort_plan.get('discount_type', EventDiscountType.PERCENTAGE)
        discount = None

        if discount_type == EventDiscountType.PERCENTAGE:
            discount = cohort_plan.get('discount')

        elif discount_type == EventDiscountType.FLAT:
            discount = NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('discount'))

        return discount

    @staticmethod
    def create_event_cohort_plan_context(event_plan_instance, cohort_plan):
        discount = PlanViewHelper.calculate_event_cohort_plan_discount(cohort_plan)

        event_cohort_plan_context = {
            'cohort_id': cohort_plan.get('cohort_id'),
            'cost': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('cost')),
            'strike_cost': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('strike_cost')),
            'cost_usd': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('cost_usd')),
            'strike_cost_usd': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('strike_cost_usd')),
            'discount_type': cohort_plan.get('discount_type'),
            'discount': discount,
            'event_plan': event_plan_instance.id
        }

        return event_cohort_plan_context

    @staticmethod
    def fetch_member_cohorts_for_event_plan(community_id, user_id):
        """
        @param community_id: Community ID
        @param user_id: User ID
        @return: list of cohort IDs he is part of
        """

        if not user_id or not community_id:
            return []

        response = CoreServiceUtilities.fetch_member_cohorts(community_id, user_id)

        if 'error_message' in response:
            error_logger.error(f'Community ID:{community_id}, User ID:{user_id}, Response:{response}')
            return []

        member_cohort_dict = response.get('member_cohorts')

        if not member_cohort_dict or not member_cohort_dict.get(str(user_id)):
            return []

        member_cohorts = [obj.get('id') for obj in member_cohort_dict.get(str(user_id))]

        return member_cohorts

    @staticmethod
    def get_member_event_cohorts(event_plan_instance: SubscriptionEventPlan, community_id, user_id):
        """
        @param event_plan_instance: SubscriptionEventPlan instance
        @param community_id: Community ID
        @param user_id: User ID
        @return: Set of Member Cohorts which are added in current Event Plan
        """

        matching_cohorts = set()

        if not event_plan_instance:
            return matching_cohorts

        if not user_id or not community_id:
            return matching_cohorts

        filters = {'event_plan_id': event_plan_instance.id}
        event_cohort_ids = list(ModelUtilities.get_model_filter(model=EventCohortPlan,
                                                                filter_dict=filters).values_list('cohort_id',
                                                                                                 flat=True))
        member_cohorts = []

        # If any EventCohortPlan exists, fetch member's cohorts and check if any cohort_id matches with user's cohorts
        if event_cohort_ids:
            member_cohorts = PlanViewHelper.fetch_member_cohorts_for_event_plan(community_id=community_id,
                                                                                user_id=user_id)

        matching_cohorts = set(member_cohorts) & set(event_cohort_ids)

        return matching_cohorts

    @staticmethod
    def fetch_event_cost(event_plan_instance: SubscriptionEventPlan, matching_cohorts):
        """
        @param event_plan_instance: SubscriptionEventPlan instance
        @param matching_cohorts: Set of Member Cohorts which are added in current Event Plan
        @return: Event cost for that user.
        """

        if not matching_cohorts:
            return event_plan_instance.cost

        filter_dict = {'event_plan_id': event_plan_instance.id, 'cohort_id__in': list(matching_cohorts)}
        member_event_plan_cohorts = ModelUtilities.get_model_filter(EventCohortPlan, filter_dict).order_by('cost')

        if not member_event_plan_cohorts:
            return event_plan_instance.cost

        return member_event_plan_cohorts[0].cost
