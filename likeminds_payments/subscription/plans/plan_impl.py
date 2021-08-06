from .constants import EVENT_PAYMENT_LINK
from ..plans.plan_manager import PlanManager
from .models import SubscriptionPlan, SubscriptionEventPlan
from .serializers import PlanSerializer, EventPlanSerializer
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities

from ..utility.plan_utilities import PlanUtilities
from ..utility.states import EventDiscountType
from django.conf import settings

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

    def _process_event_creation_plan(self, req_body):

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

    def create_plan(self) -> dict:

        response = self._generate_response_from_plan(self.get_plan_instance())

        if 'error_message' in response:
            return {'error_message': response['error_message']}

        return response

    @staticmethod
    def _fetch_plans(community_id: str):
        return SubscriptionPlan.objects.filter(community_id=community_id, is_deleted=False).order_by('created_at')

    @staticmethod
    def _serialize_plans(plans) -> list:
        return PlanSerializer(plans)

    @staticmethod
    def _serialize_event_plan_list(chatroom_ids):

        event_filter = SubscriptionEventPlan.objects.filter(chatroom_id__in=chatroom_ids).order_by('created_at')
        event_plans = [EventPlanSerializer(plan_instance) for plan_instance in event_filter]

        return event_plans

    def fetch_plan(self) -> dict:

        plans = self._fetch_plans(self.get_community_id())

        if len(plans) == 0:
            return {'error_message': 'no plans exist with provided community_id'}

        return {'plans': self._serialize_plans(plans)}

    def delete_plan(self) -> dict:

        plan_instance = self.get_plan_instance()

        if not plan_instance.plan_id:
            return {'error_message': 'issue while deleting plan object'}

        return {'success': True}

    def create_event_plan(self, req_body, member_id) -> dict:

        create_info = self._process_event_creation_plan(req_body)
        instance = SubscriptionEventPlan.create_instance(create_info)
        CoreServiceUtilities.update_event({
            'member_id': member_id,
            'chatroom_id': instance.chatroom_id,
            'event_payment_link': EVENT_PAYMENT_LINK % (settings.URL, instance.event_plan_id, instance.community_id),
            'restrict_event_update_notification': True
        })

        return {'success': True}

    def fetch_event_plan(self, chatroom_ids) -> dict:

        event_plans = self._serialize_event_plan_list(chatroom_ids)

        return {'event_plans': event_plans}
