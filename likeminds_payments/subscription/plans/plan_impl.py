from __future__ import absolute_import, unicode_literals
from .constants import EVENT_PAYMENT_LINK
from .plan_helper import PlanHelper
from ..external_services.logging.logging_wrapper import LoggingWrapper
from ..plans.plan_manager import PlanManager
from .models import SubscriptionPlan, SubscriptionEventPlan
from .serializers import PlanSerializer, EventPlanSerializer, EventCohortPlanSerializer
from ..utility.async_tasks import update_event_in_webflow_service
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.number_utilities import NumberUtilities

from ..utility.plan_utilities import PlanUtilities
from ..utility.states import EventDiscountType
from django.conf import settings

error_logger = LoggingWrapper.get_instance()


class PlanImpl(PlanManager):
    community_id = None
    plan_instance = None

    def __init__(self, community_id: str = None, plan_instance: SubscriptionPlan = None):
        self.community_id = community_id
        self.plan_instance = plan_instance

    def get_community_id(self) -> str:
        return self.community_id

    def get_plan_instance(self) -> SubscriptionPlan:
        return self.plan_instance

    @staticmethod
    def _generate_response_from_plan(plan_instance: SubscriptionPlan) -> dict:

        if not plan_instance.plan_id:
            return {'error_message': 'issue with created plan object'}

        return {'url': PlanUtilities.generate_plan_url(plan_instance.plan_id)}

    @staticmethod
    def _process_event_creation_plan(req_body):

        discount_type = req_body.get('discount_type', 0)
        discount = None

        if discount_type == EventDiscountType.PERCENTAGE:
            discount = req_body.get('discount')

        elif discount_type == EventDiscountType.FLAT:
            discount = NumberUtilities.convert_to_paisa_or_none(req_body.get('discount'))

        return {
            'chatroom_id': req_body.get('chatroom_id'),
            'community_id': req_body.get('community_id'),
            'cost': NumberUtilities.convert_to_paisa_or_none(req_body.get('cost')),
            'strike_cost': NumberUtilities.convert_to_paisa_or_none(req_body.get('strike_cost')),
            'cost_usd': NumberUtilities.convert_to_paisa_or_none(req_body.get('cost_usd')),
            'strike_cost_usd': NumberUtilities.convert_to_paisa_or_none(req_body.get('strike_cost_usd')),
            'discount_type': discount_type,
            'discount': discount
        }

    @staticmethod
    def update_event_plan_context(event_plan_instance, req_body):

        event_plan_instance.cost = NumberUtilities.convert_to_paisa_or_none(req_body.get('cost',
                                                                                         event_plan_instance.cost))
        event_plan_instance.strike_cost = NumberUtilities.convert_to_paisa_or_none(
            req_body.get('strike_cost', event_plan_instance.strike_cost))
        event_plan_instance.cost_usd = NumberUtilities.convert_to_paisa_or_none(
            req_body.get('cost_usd', event_plan_instance.cost_usd))
        event_plan_instance.strike_cost_usd = NumberUtilities.convert_to_paisa_or_none(
            req_body.get('strike_cost_usd', event_plan_instance.strike_cost_usd))

        discount_type = req_body.get('discount_type', event_plan_instance.discount_type)
        discount = event_plan_instance.discount

        if discount_type == EventDiscountType.PERCENTAGE:
            discount = req_body.get('discount', event_plan_instance.discount)

        elif discount_type == EventDiscountType.FLAT:
            discount = NumberUtilities.convert_to_paisa_or_none(req_body.get('discount',
                                                                             event_plan_instance.discount))

        event_plan_instance.discount_type = discount_type
        event_plan_instance.discount = discount

        event_plan_instance.save()

    def create_plan(self) -> dict:

        response = self._generate_response_from_plan(self.get_plan_instance())

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        return response

    @staticmethod
    def _fetch_plans(filters: dict):
        return ModelUtilities.get_model_filter(SubscriptionPlan, filters).order_by('created_at')

    @staticmethod
    def _serialize_plans(plans) -> list:
        return PlanSerializer(plans)

    @staticmethod
    def _serialize_event_plan_list(filters, user_id=None):

        event_filter = ModelUtilities.get_model_filter(SubscriptionEventPlan, filters).order_by('created_at')

        event_plans = []

        for event_plan_instance in event_filter:
            event_serializer = EventPlanSerializer(event_plan_instance)

            pricing_context = PlanHelper.get_event_plan_cost_context_based_on_event_cohort_plan(
                event_plan_instance=event_plan_instance,
                user_id=user_id
            )

            event_serializer.update(pricing_context)

            if event_serializer['discount_type'] == EventDiscountType.FLAT:
                event_serializer['discount'] = NumberUtilities.convert_to_rupee_or_none(event_plan_instance.discount)

            event_plans.append(event_serializer)

        return event_plans

    def fetch_plan(self, plan_id=None) -> dict:

        filters = {
            'is_deleted': False
        }

        if plan_id:
            filters['plan_id'] = plan_id

        if self.get_community_id():
            filters['community_id'] = self.get_community_id()

        plans = self._fetch_plans(filters)

        if len(plans) == 0:
            return {'error_message': 'no plans exist with provided details'}

        return {'plans': self._serialize_plans(plans)}

    def delete_plan(self) -> dict:

        plan_instance = self.get_plan_instance()

        if not plan_instance.plan_id:
            return {'error_message': 'issue while deleting plan object'}

        return {'success': True}

    def create_event_plan(self, req_body, member_id) -> dict:

        create_info = self._process_event_creation_plan(req_body)
        instance = SubscriptionEventPlan.create_instance(create_info)
        self._process_event_cohort_plans(cohort_plans=req_body.get('cohort_plan', []), event_plan_instance=instance)
        CoreServiceUtilities.update_event({
            'member_id': member_id,
            'chatroom_id': instance.chatroom_id,
            'event_payment_link': EVENT_PAYMENT_LINK % (
                settings.WEB_URL, instance.event_plan_id, instance.chatroom_id,
                instance.community_id),
            'restrict_event_update_notification': True
        })
        update_event_in_webflow_service.delay(instance.event_plan_id, member_id)

        CoreServiceUtilities.trigger_event_creation_mail_in_core_service(instance.chatroom_id, instance.cost)

        return {'success': True}

    def fetch_event_plan(self, filters=None, user_id=None) -> dict:

        event_plans = self._serialize_event_plan_list(filters, user_id)

        return {'event_plans': event_plans}

    def update_event_plan(self, req_body, member_id) -> dict:

        event_plan_id = req_body.get('event_plan_id')

        event_plan_filter = ModelUtilities.get_model_filter(SubscriptionEventPlan,
                                                            {'event_plan_id': event_plan_id})

        if not event_plan_filter:
            return {'error_message': "Invalid event plan id", 'success': False}

        event_plan_instance = event_plan_filter[0]
        self.update_event_plan_context(event_plan_instance, req_body)
        update_event_in_webflow_service.delay(event_plan_instance.event_plan_id, member_id)

        return {'success': True}

    @staticmethod
    def _process_event_cohort_plans(cohort_plans: list, event_plan_instance: SubscriptionEventPlan):

        if not event_plan_instance:
            return

        for cohort_plan in cohort_plans:
            event_cohort_plan_context = PlanHelper.create_event_cohort_plan_context(
                event_plan_instance=event_plan_instance,
                cohort_plan=cohort_plan
            )

            event_cohort_plan_serializer = EventCohortPlanSerializer(data=event_cohort_plan_context)

            if event_cohort_plan_serializer.is_valid():
                event_cohort_plan_serializer.save()

            else:
                error_logger.error(f' Event Plan Serializer:{event_cohort_plan_serializer.errors},'
                                   f' cohort plan data:{event_cohort_plan_context}')
