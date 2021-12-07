from celery import shared_task
from django.template.loader import get_template
import analytics

from .constants import *
from .models import SubscriptionPlan
from ..subscriptions.constants import SUBSCRIPTION_COHORT_NAME, SUBSCRIPTION_EXPIRED_COHORT_NAME
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.async_tasks import send_email_from_core_service, get_first_verified_email_and_phone
from ..utility.response_utilities import ResponseUtilities
from ..utility.states import cohort_types
from ..utility.json_utilities import JsonUtilities


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
    def _create_new_plan_instance(plan_body, user_id=0) -> dict:

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

        if 'description_icon_type' not in plan_body:
            plan_body['description_icon_type'] = None

        try:
            plan_instance = SubscriptionPlan.create_instance(plan_body)

            # Make community paid
            community_update = CoreServiceUtilities.edit_community(plan_body.get('community_id'), user_id)

            if 'error_message' in community_update:
                return {'error_message': community_update['error_message']}

            # Send first plan creation mail
            PlanViewHelper.send_email_for_first_plan_creation.delay(community_id=plan_body.get('community_id'),
                                                                    user_id=user_id)

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

            plan_instance = PlanViewHelper._create_new_plan_instance(plan_body, user_id=user_id)

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
            return {'error_message': response['error_message'],  'status_code': response['status_code']}

        return {}

    @staticmethod
    def parameter_validation_for_first_plan_creation_email(user_data, community_data, user_id):

        if not community_data.get('community'):
            return

        community_data = community_data.get('community')

        if not user_data.get('user'):
            return

        verified_email = get_first_verified_email_and_phone(user_id, user_data)

        if not verified_email.get('email'):
            return

        user_data = user_data.get('user')

        return user_data, community_data, verified_email

    @staticmethod
    def prepare_email_data_for_first_plan_creation(user_data, community_data, verified_email):

        mail_subject = FIRST_MEMBERSHIP_PLAN_CM_MAIL_SUBJECT.format(user_data.get('name'))

        cm_onboarding_branch_url = CoreServiceUtilities.get_cm_onboarding_community_feed_url(
            community_data.get('id'))

        mail_template = get_template('cm_onboarding/first_plan_creation_cm_onboarding_email.html').render({
            "community_logo": community_data.get('image_url'),
            "community_name": community_data.get('name'),
            "cm_name": user_data.get('name'),
            "community_brand_color": community_data.get('brand_color') if community_data.get('brand_color') else
            DEFAULT_CM_ONBOARDING_EMAIL_BUTTON_COLOR,
            "button_text": FIRST_MEMBERSHIP_PLAN_CM_MAIL_BUTTON_TEXT,
            "button_link": cm_onboarding_branch_url.get('feed_url') if cm_onboarding_branch_url.get('feed_url')
            else ''
        })

        mail_body = {
            'subject': mail_subject,
            'mail_body': mail_template,
            'mail_recipient_list': [verified_email.get('email')],
            'reply_to': [FIRST_MEMBERSHIP_PLAN_CM_REPLY_EMAIL]
        }

        return mail_body

    @staticmethod
    @shared_task
    def send_email_for_first_plan_creation(community_id, user_id):

        plan_filter = ModelUtilities.get_model_filter(SubscriptionPlan, {'community_id': community_id})

        if len(plan_filter) == 1:
            community_data = CoreServiceUtilities.get_community_data(community_id)
            user_data = CoreServiceUtilities.get_user_details({'member_id': user_id})

            user_data, community_data, verified_email = PlanViewHelper.parameter_validation_for_first_plan_creation_email(
                user_data, community_data, user_id)

            mail_body = PlanViewHelper.prepare_email_data_for_first_plan_creation(user_data, community_data,
                                                                                  verified_email)

            send_email_response = send_email_from_core_service(user_id, mail_body)

    @staticmethod
    def add_event_for_membership_plan(plan_serialized_object, event_name, user_id):

        days_multiplier = SUBSCRIPTION_PLAN_DAYS_MULTIPLIER.get(plan_serialized_object.get('duration_name')) if \
            plan_serialized_object.get('duration_name') in SUBSCRIPTION_PLAN_DAYS_MULTIPLIER else \
            SUBSCRIPTION_PLAN_DAYS_MULTIPLIER.get('monthly')

        plan_event_metadata = {
            'cost': plan_serialized_object.get('cost'),
            'duration_in_days': plan_serialized_object.get('duration_in_months') * days_multiplier,
            'plan_name': plan_serialized_object.get('plan_title'),
            'plan_id': plan_serialized_object.get('plan_id')
        }

        analytics.track(user_id, event_name, plan_event_metadata)
