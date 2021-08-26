from __future__ import absolute_import, unicode_literals
from celery import shared_task

from subscription.external_services.webflow.webflow_impl import WebflowImpl
from subscription.plans.constants import EVENT_PAYMENT_LINK
from subscription.plans.models import SubscriptionEventPlan
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.utility.model_utilities import ModelUtilities
from django.conf import settings


def create_event_meta_for_webflow_update(event_plan_instance):
    event_meta = {
        'fields': {
            'cost': event_plan_instance.cost,
            'payment-link': EVENT_PAYMENT_LINK % (
                settings.WEB_URL, event_plan_instance.event_plan_id, event_plan_instance.community_id)
        }
    }

    return event_meta


@shared_task
def update_event_in_webflow_service(event_plan_id, user_id):
    event_plan_filter = ModelUtilities.get_model_filter(SubscriptionEventPlan,
                                                        {'event_plan_id': event_plan_id})

    if not event_plan_filter:
        return

    event_plan_instance = event_plan_filter[0]
    webflow_item_id = None
    event_meta = create_event_meta_for_webflow_update(event_plan_instance)
    chatroom_meta = CoreServiceUtilities.chatroom_fetch({'chatroom_id': event_plan_instance.chatroom_id,
                                                         'member_id': user_id}).get('chatroom')

    if chatroom_meta and chatroom_meta.get('webflow_item_id'):
        webflow_item_id = chatroom_meta.get('webflow_item_id')

    if not webflow_item_id:
        return

    WebflowImpl.update_event_in_webflow(event_meta, webflow_item_id)
