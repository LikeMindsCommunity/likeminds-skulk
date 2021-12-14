from .models import EventCohortPlan
from ..external_services.logging.logging_wrapper import LoggingWrapper
from ..utility.model_utilities import ModelUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.plan_utilities import PlanUtilities
from ..utility.states import EventDiscountType
from ..utility.core_service_utilities import CoreServiceUtilities
from .constants import *
from ..subscriptions.constants import *

error_logger = LoggingWrapper.get_instance()


def PlanSerializer(plans) -> list:
    output = []

    for plan in plans:
        plan_object = {
            'plan_id': plan.plan_id,
            'community_id': plan.community_id,
            'name': plan.name,
            'duration_name': plan.duration_name,
            'cost': plan.cost // 100,
            'strike_cost': plan.strike_cost,
            'cost_usd': plan.cost_usd,
            'strike_cost_usd': plan.strike_cost_usd,
            'duration_in_months': plan.duration_in_months,
            'cm_emails': plan.cm_emails,
            'buddy_emails': plan.buddy_emails,
            'description': plan.description,
            'referral_free_days': plan.referral_free_days,
            'image': plan.image,
            'url': PlanUtilities.generate_plan_url(plan.plan_id)
        }

        community_data = CoreServiceUtilities.get_community_data(plan.community_id)

        if 'community' in community_data:
            plan_object['community_name'] = community_data['community'].get('name')

        if plan.strike_cost is not None:
            plan_object['strike_cost'] = plan.strike_cost // 100

        if plan.cost_usd is not None:
            plan_object['cost_usd'] = plan.cost_usd // 100

        if plan.strike_cost_usd is not None:
            plan_object['strike_cost_usd'] = plan.strike_cost_usd // 100

        if plan_object['duration_name'] == LIFETIME_PAYMENT:
            plan_object['plan_sub_title'] = '{} for {}'.format(
                plan_object['cost'],
                SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['subtitle']
            )

        else:
            plan_object['plan_sub_title'] = '{} for {} {}'.format(
                plan_object['cost'],
                plan_object['duration_in_months'],
                SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['subtitle'])

        if SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['unique']:
            plan_title = SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['title']

        else:
            plan_title = '{} "{}" Plan'.format(plan_object['duration_in_months'],
                                               SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['title'])
        plan_object['plan_title'] = plan_title

        output.append(plan_object)

    return output


def EventPlanSerializer(plan_instance, user_id=None) -> dict:
    plan_context = {
        'event_plan_id': plan_instance.event_plan_id,
        'chatroom_id': plan_instance.chatroom_id,
        'community_id': plan_instance.community_id,
        'cost': NumberUtilities.convert_to_rupee_or_none(get_event_plan_cost(plan_instance, user_id)),
        'strike_cost': NumberUtilities.convert_to_rupee_or_none(plan_instance.strike_cost),
        'cost_usd': NumberUtilities.convert_to_rupee_or_none(plan_instance.cost_usd),
        'strike_cost_usd': NumberUtilities.convert_to_rupee_or_none(plan_instance.strike_cost_usd),
        'discount_type': plan_instance.discount_type,
        'discount': plan_instance.discount
    }

    if plan_context['discount_type'] == EventDiscountType.FLAT:
        plan_context['discount'] = NumberUtilities.convert_to_rupee_or_none(plan_instance.discount)

    return plan_context


def get_event_plan_cost(event_plan_instance, user_id):

    filters = {'event_plan_id': event_plan_instance.id}
    event_cohort_ids = list(ModelUtilities.get_model_filter(model=EventCohortPlan,
                                                            filter_dict=filters).values_list('cohort_id', flat=True))

    if not user_id or not event_cohort_ids:
        return event_plan_instance.cost

    response = CoreServiceUtilities.fetch_member_cohorts(event_plan_instance.community_id, user_id)

    if 'error_message' in response:
        error_logger.error(f'Community ID:{event_plan_instance.community_id}, User ID:{user_id}, Response:{response}')
        return event_plan_instance.cost

    member_cohort_dict = response.get('member_cohorts')
    member_cohorts = set()

    if member_cohort_dict.get(user_id):
        member_cohorts = [obj.get('id') for obj in member_cohort_dict.get(user_id)]

    matching_cohorts = set(member_cohorts) & set(event_cohort_ids)
    filter_dict = {'event_plan_id': event_plan_instance.id, 'cohort_id__in': list(matching_cohorts)}
    member_event_plan_cohorts = ModelUtilities.get_model_filter(EventCohortPlan, filter_dict).order_by('cost')

    if not member_event_plan_cohorts:
        return event_plan_instance.cost

    return member_event_plan_cohorts[0].cost
