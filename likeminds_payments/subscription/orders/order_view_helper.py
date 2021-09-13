from ..plans.models import SubscriptionPlan, SubscriptionEventPlan
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.request_utilities import RequestUtilities
from ..external_services.razorpay.razorpay_wrapper import RazorpayWrapper
from .constants import *
from ..utility.states import MemberState, EventDiscountType


class OrderViewHelper:

    @staticmethod
    def create_order_body_validator(request_body) -> dict:

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'plan_id' not in request_body or not request_body['plan_id']:
            return {'error_message': 'send plan_id'}

        if 'payment_page_url' not in request_body or not request_body['payment_page_url']:
            return {'error_message': 'send payment_page_url'}

        return request_body

    @staticmethod
    def _create_order_object_data(plan_instance: SubscriptionPlan, order_body: dict, community_data: dict) -> dict:

        order_data = {
            "amount": plan_instance.cost,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "plan_id": plan_instance.plan_id,
                "community_name": community_data['name'],
                "name": plan_instance.name,
                "cm_emails": plan_instance.cm_emails,
                "payment_page_url": order_body['payment_page_url'],
                "renew": False,
                "grace_period": 0,
                "community_id": plan_instance.community_id,
                "duration_in_months": plan_instance.duration_in_months,
                "duration_name": plan_instance.duration_name,
                "type": "Subscription",
                "event_time": '',
                "join_link": ''
            }
        }

        if 'country_code' in order_body and order_body['country_code'] != INDIA_CODE:
            if plan_instance.cost_usd is not None:
                order_data['amount'] = plan_instance.cost_usd
                order_data['currency'] = USD_CURRENCY

        if 'renew' in order_body:
            order_data['notes']['renew'] = order_body['renew']

        if 'user_id' in order_body:
            order_data['notes']['user_id'] = order_body['user_id']

        if 'shared_by' in order_body:
            order_data['notes']['shared_by'] = order_body['shared_by']

        if 'grace_period' in community_data:
            order_data['notes']['grace_period'] = community_data['grace_period']

        return order_data

    @staticmethod
    def create_order_instance_helper(order_body) -> dict:

        plan_instance = SubscriptionPlan.get_plan_or_None(order_body['plan_id'])

        if not plan_instance:
            return {'error_message': 'invalid plan_id'}

        if plan_instance.is_deleted:
            return {'error_message': 'plan no longer exists'}

        community_data = CoreServiceUtilities.get_community_data(plan_instance.community_id)

        if 'error_message' in community_data:
            return {'error_message': community_data['error_message']}

        order_data = OrderViewHelper._create_order_object_data(plan_instance, order_body, community_data['community'])

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.create(data=order_data)

        if 'error_message' in order_instance:
            return {'error_message': 'error creating order with razorpay'}

        return {'order_instance': order_instance}

    @staticmethod
    def verify_order_body_validator(request_body):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if 'order_id' not in request_body or not request_body['order_id']:
            return {'error_message': 'send order_id'}

        if 'razorpay_order_id' not in request_body or not request_body['razorpay_order_id']:
            return {'error_message': 'send razorpay_order_id'}

        if request_body['razorpay_order_id'] != request_body['order_id']:
            return {'error_message': 'order_id not matching with razorpay_order_id'}

        if 'razorpay_payment_id' not in request_body or not request_body['razorpay_payment_id']:
            return {'error_message': 'send razorpay_payment_id'}

        if 'razorpay_signature' not in request_body or not request_body['razorpay_signature']:
            return {'error_message': 'send razorpay_signature'}

        return request_body

    @staticmethod
    def verify_order_instance_helper(payment_body) -> dict:

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.fetch(payment_body['order_id'])

        if not order_instance:
            return {'error_message': 'invalid razorpay_order_id'}

        return {'order_instance': order_instance}

    @staticmethod
    def create_event_order_body_validator(request_body) -> dict:

        if not request_body:

            return {'error_message': 'invalid request body'}

        if not request_body.get('event_plan_id'):

            return {'error_message': 'send event_plan_id'}

        if not request_body.get('payment_page_url'):

            return {'error_message': 'send payment_page_url'}

        if not request_body.get('user_id'):

            return {'error_message': 'Invalid user id'}

        return request_body

    @staticmethod
    def _create_event_order_object_data(plan_instance, order_body, community_data) -> dict:

        order_data = {
            "amount": plan_instance.cost,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "event_plan_id": plan_instance.event_plan_id,
                "community_id": plan_instance.community_id,
                "community_name": community_data['name'],
                "payment_page_url": order_body['payment_page_url'],
                "type": "event",
                "user_id": order_body['user_id'],
                "event_time": '',
                "join_link": ''
            }
        }

        return order_data

    @staticmethod
    def create_event_order_instance_helper(order_body) -> dict:

        plan_instance = SubscriptionEventPlan.get_event_plan_or_None(order_body.get('event_plan_id'))

        if not plan_instance:
            return {'error_message': 'invalid event_plan_id'}

        community_data = CoreServiceUtilities.get_community_data(plan_instance.community_id)

        if community_data.get('error_message'):
            return {'error_message': community_data['error_message']}

        order_data = OrderViewHelper._create_event_order_object_data(plan_instance, order_body,
                                                                     community_data['community'])

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.create(data=order_data)

        if order_instance.get('error_message'):
            return {'error_message': 'error creating order with razorpay'}

        return {'order_instance': order_instance}

    @staticmethod
    def get_cost_for_event(plan_instance, user_id) -> int:

        member_state = CoreServiceUtilities.get_member_state(plan_instance.community_id, user_id)
        cost = plan_instance.cost

        if member_state in [MemberState.MEMBER, MemberState.PROFILE_UNAVAILABLE]:

            if plan_instance.discount and plan_instance.discount_type:

                if plan_instance.discount_type == EventDiscountType.PERCENTAGE:
                    cost = NumberUtilities.get_n_percentage_value(cost, plan_instance.discount)

                elif plan_instance.discount_type == EventDiscountType.FLAT:
                    cost = cost - plan_instance.discount

        return cost

    @staticmethod
    def create_community_event_order_body_validator(request_body) -> dict:

        if not request_body:

            return {'error_message': 'invalid request body'}

        if not request_body.get('event_plan_id'):

            return {'error_message': 'send event_plan_id'}

        if not request_body.get('payment_page_url'):

            return {'error_message': 'send payment_page_url'}

        if not request_body.get('user_id'):

            return {'error_message': 'Invalid user id'}

        if not request_body.get('plan_id'):

            return {'error_message': 'Invalid plan id'}

        return request_body

    @staticmethod
    def create_community_event_order_instance_helper(order_body) -> dict:

        event_plan_instance = SubscriptionEventPlan.get_event_plan_or_None(order_body.get('event_plan_id'))

        if not event_plan_instance:
            return {'error_message': 'invalid event_plan_id'}

        community_data = CoreServiceUtilities.get_community_data(event_plan_instance.community_id)

        community_plan_instance = SubscriptionPlan.get_plan_or_None(order_body.get('plan_id'))

        if event_plan_instance.community_id != community_plan_instance.community_id:
            return {'error_message': 'plan_id and event_plan_id should belong to same community'}

        if community_data.get('error_message'):
            return {'error_message': community_data['error_message']}

        cost = OrderViewHelper.get_cost_for_event_in_community_event_order(event_plan_instance,
                                                                           order_body.get('user_id'))

        total_cost = cost + community_plan_instance.cost

        order_data = OrderViewHelper._create_community_event_order_object_data(event_plan_instance,
                                                                               community_plan_instance,
                                                                               order_body,
                                                                               community_data['community'],
                                                                               total_cost)

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.create(data=order_data)

        if order_instance.get('error_message'):
            return {'error_message': 'error creating order with razorpay'}

        return {'order_instance': order_instance}

    @staticmethod
    def _create_community_event_order_object_data(event_plan_instance, community_plan_instance,
                                                  order_body, community_data, amount=0) -> dict:

        order_data = {
            "amount": amount,
            "currency": "INR",
            "notes": {
                "event_plan_id": event_plan_instance.event_plan_id,
                "plan_id": community_plan_instance.plan_id,
                "name": community_plan_instance.name,
                "community_id": community_plan_instance.community_id,
                "community_name": community_data['name'],
                "type": "community_and_event",
                "payment_page_url": order_body['payment_page_url'],
                "user_id": order_body['user_id'],
            }
        }

        return order_data

    @staticmethod
    def get_cost_for_event_in_community_event_order(event_plan_instance, user_id) -> int:

        member_state = CoreServiceUtilities.get_member_state(event_plan_instance.community_id, user_id)
        cost = event_plan_instance.cost

        if member_state != MemberState.GUEST:

            if event_plan_instance.discount and event_plan_instance.discount_type:

                if event_plan_instance.discount_type == EventDiscountType.PERCENTAGE:
                    cost = NumberUtilities.get_n_percentage_value(cost, event_plan_instance.discount)

                elif event_plan_instance.discount_type == EventDiscountType.FLAT:
                    cost = cost - event_plan_instance.discount

        return cost
