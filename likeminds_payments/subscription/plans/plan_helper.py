from subscription.external_services.logging.logging_wrapper import LoggingWrapper
from subscription.plans.models import EventCohortPlan, SubscriptionEventPlan
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
        matching_cohorts = PlanHelper.get_member_event_cohorts(event_plan_instance=event_plan_instance,
                                                               community_id=event_plan_instance.community_id,
                                                               user_id=user_id)

        pricing_context = PlanHelper.fetch_cohort_plan_cost_and_discount_context(event_plan_instance,
                                                                                 matching_cohorts)

        return pricing_context
