from ..plans.models import SubscriptionPlan, SubscriptionEventPlan, EventCohortPlan
from ..payment_page.models import PaymentPageMeta
from ..payment_page.constants import PAYMENT_PAGE_AMOUNT_TYPE_FIXED
from ..subscriptions.constants import STATUS_EXPIRED
from ..subscriptions.models import Subscription
from ..subscriptions.serializers import SubscriptionSerializer
from ..subscriptions.subscription_impl import SubscriptionImpl
from ..utility.core_service_utilities import CoreServiceUtilities
from ..utility.model_utilities import ModelUtilities
from ..utility.number_utilities import NumberUtilities
from ..utility.request_utilities import RequestUtilities
from ..utility.url_utilities import UrlUtilities
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
    def _create_event_order_object_data(plan_instance, order_body, community_data, amount=None) -> dict:

        if amount is None:
            amount = plan_instance.cost

        order_data = {
            "amount": amount,
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

        member_state = CoreServiceUtilities.get_member_state(community_data['community']['id'],
                                                             order_body.get('user_id'))

        # Fetch EventCohortPlan related to this Plan
        filters = {'event_plan_id': plan_instance.id}
        event_cohort_ids = list(ModelUtilities.get_model_filter(model=EventCohortPlan,
                                                                filter_dict=filters).values_list('cohort_id',
                                                                                                 flat=True))
        member_cohorts = []

        # If any EventCohortPlan exists, fetch member's cohorts and check if any cohort_id matches with user's cohorts
        if event_cohort_ids:
            member_cohorts = OrderViewHelper.fetch_member_cohorts_for_create_event_order(
                community_id=community_data['community']['id'], user_id=order_body.get('user_id'))

        matching_cohorts = set(member_cohorts) & set(event_cohort_ids)

        subscription = Subscription.get_subscription_or_None(user_id=order_body.get('user_id'),
                                                             community_id=community_data['community']['id'])
        subscription_object = None

        if subscription:
            subscription_objects = SubscriptionSerializer([subscription])

            if subscription_objects:
                subscription_object = subscription_objects[0]

        if (member_state == MemberState.GUEST) and plan_instance.strike_cost:
            amount = plan_instance.strike_cost

        elif matching_cohorts:
            filter_dict = {'event_plan_id': plan_instance.id, 'cohort_id__in': list(matching_cohorts)}
            member_event_plan_cohorts = ModelUtilities.get_model_filter(EventCohortPlan, filter_dict).order_by('cost')
            amount = member_event_plan_cohorts[0].cost

        elif subscription_object and (subscription_object.get('membership_state') == STATUS_EXPIRED) and plan_instance.strike_cost:
            amount = plan_instance.strike_cost

        else:
            amount = plan_instance.cost

        order_data = OrderViewHelper._create_event_order_object_data(plan_instance, order_body,
                                                                     community_data['community'],
                                                                     amount=amount)

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

        event_plan_filter = ModelUtilities.get_model_filter(SubscriptionEventPlan,
                                                            {'event_plan_id': order_body.get('event_plan_id')})

        if not event_plan_filter:
            return {'error_message': 'invalid event_plan_id'}

        event_plan_instance = event_plan_filter[0]

        community_data = CoreServiceUtilities.get_community_data(event_plan_instance.community_id)

        community_plan_filter = ModelUtilities.get_model_filter(SubscriptionPlan,
                                                                {'plan_id': order_body.get('plan_id')})

        if not community_plan_filter:
            return {'error_message': 'invalid plan_id'}

        community_plan_instance = community_plan_filter[0]

        if event_plan_instance.community_id != community_plan_instance.community_id:
            return {'error_message': 'plan_id and event_plan_id should belong to same community'}

        if community_data.get('error_message'):
            return {'error_message': community_data['error_message']}

        filters = {'event_plan_id': event_plan_instance.id}
        event_cohort_ids = list(ModelUtilities.get_model_filter(model=EventCohortPlan,
                                                                filter_dict=filters).values_list('cohort_id',
                                                                                                 flat=True))
        member_cohorts = []

        # If any EventCohortPlan exists, fetch member's cohorts and check if any cohort_id matches with user's cohorts
        if event_cohort_ids:
            member_cohorts = OrderViewHelper.fetch_member_cohorts_for_create_event_order(
                community_id=community_data['community']['id'], user_id=order_body.get('user_id'))

        matching_cohorts = set(member_cohorts) & set(event_cohort_ids)

        event_cost = event_plan_instance.cost

        # If he is a part of cohort, fetch minimum cost from related EventCohortPlan instances
        if matching_cohorts:
            filter_dict = {'event_plan_id': event_plan_instance.id, 'cohort_id__in': list(matching_cohorts)}
            member_event_plan_cohorts = ModelUtilities.get_model_filter(EventCohortPlan, filter_dict).order_by('cost')

            if member_event_plan_cohorts:
                event_cost = member_event_plan_cohorts[0].cost

        total_cost = event_cost + community_plan_instance.cost

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

        if 'renew' in order_body:
            order_data['notes']['renew'] = order_body['renew']

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

    @staticmethod
    def create_payment_page_order_body_validator(request_body) -> dict:

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not request_body.get('payment_page_id'):
            return {'error_message': 'send payment_page_id'}

        if not request_body.get('payment_page_url'):
            return {'error_message': 'send payment_page_url'}

        if not request_body.get('payment_name'):
            return {'error_message': 'send payment_name'}

        if not request_body.get('amount'):
            return {'error_message': 'send amount'}

        return request_body

    @staticmethod
    def _create_payment_page_order_object_data(payment_page_instance, order_body, community_data, amount=0) -> dict:

        order_data = {
            "amount": amount,
            "currency": "INR",
            "notes": {
                "payment_page_id": payment_page_instance.payment_page_id,
                "community_id": community_data['id'],
                "community_name": community_data['name'],
                "type": "payment_page",
                "payment_page_url": UrlUtilities.extract_part_from_url(payment_page_instance.payment_page_url,
                                                                       'path', init_slash_off=True),
                "payment_name": order_body['payment_name'],
            }
        }

        return order_data

    @staticmethod
    def create_payment_page_order_instance_helper(order_body) -> dict:

        payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                              {"payment_page_id": order_body.get('payment_page_id')})

        if not payment_page_filter:
            return {'error_message': 'invalid payment_page_id'}

        payment_page_instance = payment_page_filter[0]

        community_data = CoreServiceUtilities.get_community_data(payment_page_instance.community_id)

        if community_data.get('error_message'):
            return {'error_message': community_data['error_message']}

        if payment_page_instance.amount_type == PAYMENT_PAGE_AMOUNT_TYPE_FIXED:
            amount = payment_page_instance.amount

        else:
            amount = order_body['amount']

        order_data = OrderViewHelper._create_payment_page_order_object_data(payment_page_instance,
                                                                            order_body,
                                                                            community_data['community'],
                                                                            amount)

        razorpay_client = RazorpayWrapper.get_instance()

        order_instance = razorpay_client.order.create(data=order_data)

        if order_instance.get('error_message'):
            return {'error_message': 'error creating order with razorpay'}

        return {'order_instance': order_instance}

    @staticmethod
    def fetch_member_cohorts_for_create_event_order(community_id, user_id):
        """
        @param community_id: Community ID
        @param user_id: User ID
        @return: list of cohort IDs he is part of
        """

        if not user_id or not community_id:
            return []

        response = CoreServiceUtilities.fetch_member_cohorts(community_id, user_id)

        if 'error_message' in response:
            print(f'Community ID:{community_id}, User ID:{user_id}, Response:{response}')
            return []

        member_cohort_dict = response.get('member_cohorts')

        if not member_cohort_dict or not member_cohort_dict.get(user_id):
            return []

        member_cohorts = [obj.get('id') for obj in member_cohort_dict.get(user_id)]

        return member_cohorts

