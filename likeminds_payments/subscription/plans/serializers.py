from rest_framework import serializers

from .models import EventCohortPlan
from .plan_helper import PlanHelper
from ..external_services.logging.logging_wrapper import LoggingWrapper
from ..utility.number_utilities import NumberUtilities
from ..utility.plan_utilities import PlanUtilities
from ..utility.core_service_utilities import CoreServiceUtilities
from .constants import *
from ..subscriptions.constants import *

error_logger = LoggingWrapper.get_instance()


class EventCohortPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCohortPlan
        fields = '__all__'


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


def EventPlanSerializer(plan_instance) -> dict:
    plan_context = {
        'event_plan_id': plan_instance.event_plan_id,
        'chatroom_id': plan_instance.chatroom_id,
        'community_id': plan_instance.community_id,
        'cost': NumberUtilities.convert_to_rupee_or_none(plan_instance.cost),
        'strike_cost': NumberUtilities.convert_to_rupee_or_none(plan_instance.strike_cost),
        'cost_usd': NumberUtilities.convert_to_rupee_or_none(plan_instance.cost_usd),
        'strike_cost_usd': NumberUtilities.convert_to_rupee_or_none(plan_instance.strike_cost_usd),
        'discount_type': plan_instance.discount_type,
        'discount': plan_instance.discount
    }

    return plan_context

