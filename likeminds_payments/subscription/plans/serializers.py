from ..utility.number_utilities import NumberUtilities
from ..utility.plan_utilities import PlanUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.states import EventDiscountType
from ..utility.core_service_utilities import CoreServiceUtilities
from .constants import *
from ..subscriptions.constants import *
from rest_framework import serializers
from .models import SamplePlanCategory, SamplePlan


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
            'url': PlanUtilities.generate_plan_url(plan.plan_id),
            'description_icon_type': plan.description_icon_type
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

        if plan.name:
            plan_title = plan.name

        elif SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['unique']:
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

    if plan_context['discount_type'] == EventDiscountType.FLAT:
        plan_context['discount'] = NumberUtilities.convert_to_rupee_or_none(plan_instance.discount)

    return plan_context


class SamplePlanCategorySerializers(serializers.ModelSerializer):

    class Meta:
        model = SamplePlanCategory
        fields = ('id', 'name', 'image_url')

    def __init__(self, *args, **kwargs):
        super(SamplePlanCategorySerializers, self).__init__(*args, **kwargs)

    def to_representation(self, sample_plan_category):
        data = super(SamplePlanCategorySerializers, self).to_representation(sample_plan_category)

        fields = self._readable_fields

        for field in fields:

            if data[field.field_name] is None:
                del data[field.field_name]

        return data

    @staticmethod
    def update_instance(instance, create_info):
        instance.name = create_info.get('name') if create_info.get('name') else instance.name
        instance.image_url = create_info.get('image_url') if create_info.get('image_url') else instance.image_url
        instance.save()

        return instance


class SamplePlanSerializers(serializers.ModelSerializer):
    class Meta:
        model = SamplePlan
        fields = ('id', 'name', 'description', 'duration_name', 'duration_in_months', 'cost', 'strike_cost',
                  'category')

    def __init__(self, *args, **kwargs):
        super(SamplePlanSerializers, self).__init__(*args, **kwargs)

    def to_representation(self, sample_plan):
        data = super(SamplePlanSerializers, self).to_representation(sample_plan)

        data['category'] = SamplePlanCategorySerializers(ModelUtilities.get_model_instance_or_none(
            SamplePlanCategory, sample_plan.category_id), many=False).data

        fields = self._readable_fields

        for field in fields:

            if data[field.field_name] is None:
                del data[field.field_name]

        return data

    @staticmethod
    def update_instance(instance, create_info):
        instance.name = create_info.get('name') if create_info.get('name') else instance.name
        instance.description = create_info.get('description') if create_info.get(
            'description') else instance.description
        instance.duration_name = create_info.get('duration_name') if create_info.get(
            'duration_name') else instance.duration_name
        instance.duration_in_months = create_info.get('duration_in_months') if create_info.get('duration_in_months') \
            else instance.duration_in_months
        instance.cost = create_info.get('cost') if create_info.get('cost') else instance.cost
        instance.strike_cost = create_info.get('strike_cost') if create_info.get(
            'strike_cost') else instance.strike_cost
        instance.category = create_info.get('category_instance') if create_info.get('category_instance') else \
            instance.category
        instance.save()

        return instance
