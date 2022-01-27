from subscription.external_services.logging.logging_wrapper import LoggingWrapper
from subscription.plans.constants import SUBSCRIPTION_PLAN_NAMES, FREE_PLAN_TITLE, FREE_TRIAL_TITLE
from subscription.plans.models import EventCohortPlan, SubscriptionEventPlan, SubscriptionPlan
from subscription.subscriptions.constants import LIFETIME_PAYMENT
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.number_utilities import NumberUtilities
from subscription.utility.states import EventDiscountType

error_logger = LoggingWrapper.get_instance()


class PlanHelper:

    @staticmethod
    def calculate_event_cohort_plan_discount(cohort_plan):
        discount_type = cohort_plan.get('discount_type', EventDiscountType.PERCENTAGE)
        discount = None

        if discount_type == EventDiscountType.PERCENTAGE:
            discount = cohort_plan.get('discount')

        elif discount_type == EventDiscountType.FLAT:
            discount = NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('discount'))

        return discount

    @staticmethod
    def create_event_cohort_plan_context(event_plan_instance, cohort_plan):
        discount = PlanHelper.calculate_event_cohort_plan_discount(cohort_plan)

        event_cohort_plan_context = {
            'cohort_id': cohort_plan.get('cohort_id'),
            'cost': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('cost')),
            'strike_cost': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('strike_cost')),
            'cost_usd': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('cost_usd')),
            'strike_cost_usd': NumberUtilities.convert_to_paisa_or_none(cohort_plan.get('strike_cost_usd')),
            'discount_type': cohort_plan.get('discount_type'),
            'discount': discount,
            'event_plan': event_plan_instance.id
        }

        return event_cohort_plan_context

    @staticmethod
    def fetch_member_cohorts_for_event_plan(community_id, user_id):
        """
        @param community_id: Community ID
        @param user_id: User ID
        @return: list of cohort IDs he is part of
        """

        if not user_id or not community_id:
            return []

        response = CoreServiceUtilities.fetch_member_cohorts(community_id, user_id)

        if 'error_message' in response:
            error_logger.error(f'Community ID:{community_id}, User ID:{user_id}, Response:{response}')
            return []

        member_cohort_dict = response.get('member_cohorts')

        if not member_cohort_dict or not member_cohort_dict.get(str(user_id)):
            return []

        member_cohorts = [obj.get('id') for obj in member_cohort_dict.get(str(user_id))]

        return member_cohorts

    @staticmethod
    def get_member_event_cohorts(event_plan_instance: SubscriptionEventPlan, community_id, user_id):
        """
        @param event_plan_instance: SubscriptionEventPlan instance
        @param community_id: Community ID
        @param user_id: User ID
        @return: Set of Member Cohorts which are added in current Event Plan
        """

        matching_cohorts = set()

        if not event_plan_instance:
            return matching_cohorts

        if not user_id or not community_id:
            return matching_cohorts

        filters = {'event_plan_id': event_plan_instance.id}
        event_cohort_ids = list(ModelUtilities.get_model_filter(model=EventCohortPlan,
                                                                filter_dict=filters).values_list('cohort_id',
                                                                                                 flat=True))
        member_cohorts = []

        # If any EventCohortPlan exists, fetch member's cohorts and check if any cohort_id matches with user's cohorts
        if event_cohort_ids:
            member_cohorts = PlanHelper.fetch_member_cohorts_for_event_plan(community_id=community_id,
                                                                            user_id=user_id)

        matching_cohorts = set(member_cohorts) & set(event_cohort_ids)

        return matching_cohorts

    @staticmethod
    def fetch_event_cost(event_plan_instance: SubscriptionEventPlan, matching_cohorts):
        """
        @param event_plan_instance: SubscriptionEventPlan instance
        @param matching_cohorts: Set of Member Cohorts which are added in current Event Plan
        @return: Event cost for that user.
        """

        if not matching_cohorts:
            return event_plan_instance.cost

        filter_dict = {'event_plan_id': event_plan_instance.id, 'cohort_id__in': list(matching_cohorts)}
        member_event_plan_cohorts = ModelUtilities.get_model_filter(EventCohortPlan, filter_dict).order_by('cost')

        if not member_event_plan_cohorts:
            return event_plan_instance.cost

        return member_event_plan_cohorts[0].cost

    @staticmethod
    def fetch_cohort_plan_cost_and_discount_context(event_plan_instance: SubscriptionEventPlan, matching_cohorts):
        """
        @param event_plan_instance: SubscriptionEventPlan instance
        @param matching_cohorts: Set of Member Cohorts which are added in current Event Plan
        @return: Event cost context for that user.
        """

        pricing_context = {
            'cost': NumberUtilities.convert_to_rupee_or_none(event_plan_instance.cost),
            'discount': event_plan_instance.discount,
            'discount_type': event_plan_instance.discount_type,
        }

        # Return Context for that user.
        if not matching_cohorts:
            return pricing_context

        filter_dict = {'event_plan_id': event_plan_instance.id, 'cohort_id__in': list(matching_cohorts)}
        member_event_plan_cohorts = ModelUtilities.get_model_filter(EventCohortPlan, filter_dict).order_by('cost')

        if not member_event_plan_cohorts:
            return pricing_context

        pricing_context['cost'] = NumberUtilities.convert_to_rupee_or_none(member_event_plan_cohorts[0].cost)
        pricing_context['discount'] = member_event_plan_cohorts[0].discount
        pricing_context['discount_type'] = member_event_plan_cohorts[0].discount_type

        return pricing_context

    @staticmethod
    def get_event_plan_cost_context_based_on_event_cohort_plan(event_plan_instance: SubscriptionEventPlan, user_id):
        """
        @param event_plan_instance: SubscriptionEventPlan instance
        @param user_id: User ID
        @return: Dictionary of Cost, Discount and Discount for that user.
        """

        matching_cohorts = PlanHelper.get_member_event_cohorts(event_plan_instance=event_plan_instance,
                                                               community_id=event_plan_instance.community_id,
                                                               user_id=user_id)

        pricing_context = PlanHelper.fetch_cohort_plan_cost_and_discount_context(event_plan_instance,
                                                                                 matching_cohorts)

        return pricing_context

    @staticmethod
    def get_plan_title_for_paid_plan(plan_object: dict, plan_instance: SubscriptionPlan):
        """
        This method fetches plan title for paid plan
        @param plan_object: Dictionary containing plan data
        @param plan_instance: SubscriptionPlan instance
        @return: str: Plan Title
        """
        if plan_instance.name:
            plan_title = plan_instance.name

        elif SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['unique']:
            plan_title = SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['title']

        else:
            plan_title = '{} "{}" Plan'.format(plan_object['duration_in_months'],
                                               SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['title'])

        return plan_title

    @staticmethod
    def get_plan_sub_title_for_paid_plan(plan_object: dict):
        """
        This method fetches plan sub title for paid plan
        @param plan_object: Dictionary containing plan data
        @return: str: Plan Sub Title
        """
        if plan_object['duration_name'] == LIFETIME_PAYMENT:
            plan_sub_title = '{} for {}'.format(
                plan_object['cost'],
                SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['subtitle']
            )

        else:
            plan_sub_title = '{} for {} {}'.format(
                plan_object['cost'],
                plan_object['duration_in_months'],
                SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['subtitle'])

        return plan_sub_title

    @staticmethod
    def get_plan_title_for_free_plan(plan_object: dict, plan_instance: SubscriptionPlan):
        """
        This method fetches plan title for free plan
        @param plan_object: Dictionary containing plan data
        @param plan_instance: SubscriptionPlan instance
        @return: str: Plan Title
        """
        if plan_instance.name:
            plan_title = plan_instance.name

        elif plan_object['duration_name'] == LIFETIME_PAYMENT:
            plan_title = FREE_PLAN_TITLE

        else:
            plan_title = FREE_TRIAL_TITLE

        return plan_title

    @staticmethod
    def get_plan_sub_title_for_free_plan(plan_object: dict):
        """
        This method fetches plan sub title for free plan
        @param plan_object: Dictionary containing plan data
        @return: str: Plan Sub Title
        """
        if plan_object['duration_name'] == LIFETIME_PAYMENT:
            plan_sub_title = '0 for {}'.format(
                SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['subtitle']
            )

        else:
            plan_sub_title = '0 for {} {}'.format(
                plan_object['duration_in_months'],
                SUBSCRIPTION_PLAN_NAMES[plan_object['duration_name']]['subtitle']
            )

        return plan_sub_title

    @staticmethod
    def get_plan_title_and_subtitle_for_plan(plan_object: dict, plan_instance: SubscriptionPlan):
        """
        This method fetches plan sub title for free plan
        @param plan_object: Dictionary containing plan data
        @param plan_instance: SubscriptionPlan instance
        @return: dict: Dictionary containing plan title and plan sub title for valid instance
        """

        plan_title_context = dict()

        if not plan_instance or not plan_object:
            return plan_title_context

        if not plan_instance.is_paid:
            plan_title = PlanHelper.get_plan_title_for_free_plan(plan_object=plan_object, plan_instance=plan_instance)
            plan_sub_title = PlanHelper.get_plan_sub_title_for_free_plan(plan_object=plan_object)

        else:
            plan_title = PlanHelper.get_plan_title_for_paid_plan(plan_object=plan_object, plan_instance=plan_instance)
            plan_sub_title = PlanHelper.get_plan_sub_title_for_paid_plan(plan_object=plan_object)

        plan_title_context = {'plan_title': plan_title, 'plan_sub_title': plan_sub_title}

        return plan_title_context
