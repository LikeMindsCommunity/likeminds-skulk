from rest_framework import serializers

from .models import BillingPlan, EventCohortPlan, TierPlan
from .plan_helper import PlanHelper
from ..external_services.logging.logging_wrapper import LoggingWrapper
from ..utility.number_utilities import NumberUtilities
from ..utility.plan_utilities import PlanUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.states import EventDiscountType
from ..utility.core_service_utilities import CoreServiceUtilities
from .constants import *
from ..subscriptions.constants import *
from rest_framework import serializers
from .models import SamplePlanCategory, SamplePlan

error_logger = LoggingWrapper.get_instance()


class EventCohortPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCohortPlan
        fields = ('id', 'cohort_id', 'cost', 'strike_cost', 'cost_usd', 'strike_cost_usd', 'discount_type', 'discount',
                  'event_plan')

    def to_representation(self, event_plan_instance):
        data = super(EventCohortPlanSerializer, self).to_representation(event_plan_instance)

        fields = self._readable_fields

        for field in fields:
            if field.field_name == 'cost':
                data['cost'] = NumberUtilities.convert_to_rupee_or_none(event_plan_instance.cost)

            if field.field_name == 'strike_cost':
                data['strike_cost'] = NumberUtilities.convert_to_rupee_or_none(event_plan_instance.strike_cost)

            if field.field_name == 'cost_usd':
                data['cost_usd'] = NumberUtilities.convert_to_rupee_or_none(event_plan_instance.cost_usd)

            if field.field_name == 'strike_cost_usd':
                data['strike_cost_usd'] = NumberUtilities.convert_to_rupee_or_none(event_plan_instance.strike_cost_usd)

            if field.field_name == 'event_plan':
                del data['event_plan']

        if data['discount_type'] == EventDiscountType.FLAT:
            data['discount'] = NumberUtilities.convert_to_rupee_or_none(data.get('discount'))

        return data


def PlanSerializer(plan) -> dict:
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
        'description_icon_type': plan.description_icon_type,
        'is_paid': plan.is_paid
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

    return plan_object


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

 # Serialiser for billing plan

class BillingPlanSerializers(serializers.ModelSerializer):
    class Meta:
        model = BillingPlan
        fields = ['tier_type']

class TierPlanSerializers(serializers.ModelSerializer):
    class Meta:
        model = TierPlan
        fields = '__all__'


 