from subscription.transactions.models import Transaction
from subscription.plans.models import SubscriptionPlan, SubscriptionEventPlan
from subscription.payment_page.models import PaymentPageMeta
from subscription.settlements.serializers import SettlementSerializer
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.states import TransactionType
from django.db.models import Sum, Min
import uuid


def get_communities():

    community_ids = []

    transactions = ModelUtilities.get_model_filter(Transaction, {}).distinct('plan_id')

    for transaction in transactions:
        plan = None

        if transaction.type == TransactionType.COMMUNITY_SUBSCRIPTION:
            plan = ModelUtilities.get_model_filter(SubscriptionPlan, {'plan_id': transaction.plan_id})

        if transaction.type == TransactionType.EVENT:
            plan = ModelUtilities.get_model_filter(SubscriptionEventPlan, {'event_plan_id': transaction.plan_id})

        if transaction.type == TransactionType.PAYMENT_PAGE:
            plan = ModelUtilities.get_model_filter(PaymentPageMeta, {'payment_page_id': transaction.plan_id})

        if not plan:
            continue

        community_id = plan[0].community_id

        if community_id not in community_ids:
            community_ids.append(community_id)

    return community_ids


def get_revenue_for_communities():

    revenue_data = {}
    epoch_31_dec_2021 = 1640932199000   # for transactions on or before 31st december 2021

    communities = get_communities()

    for community_id in communities:
        valid_plan_ids = []

        subscription_plans = ModelUtilities.get_model_filter(SubscriptionPlan, {'community_id': community_id})

        for plan in subscription_plans:
            if plan.plan_id not in valid_plan_ids:
                valid_plan_ids.append(plan.plan_id)

        event_plans = ModelUtilities.get_model_filter(SubscriptionEventPlan, {'community_id': community_id})

        for plan in event_plans:
            if plan.event_plan_id not in valid_plan_ids:
                valid_plan_ids.append(plan.event_plan_id)

        payment_pages_meta = ModelUtilities.get_model_filter(PaymentPageMeta, {'community_id': community_id})

        for plan in payment_pages_meta:
            if plan.payment_page_id not in valid_plan_ids:
                valid_plan_ids.append(plan.payment_page_id)

        transactions = ModelUtilities.get_model_filter(
            Transaction, {'plan_id__in': valid_plan_ids, 'status': 'captured', 'created_at__lte': epoch_31_dec_2021}
        ).exclude(method__in=['migration', 'manual_payment_page'])

        revenue = transactions.values('status').annotate(revenue=Sum('amount'), start_date=Min('created_at'))

        revenue_data[community_id] = {}
        revenue_data[community_id]['valid_plan_ids'] = valid_plan_ids
        revenue_data[community_id]['revenue'] = revenue[0].get('revenue') if len(transactions) else 0
        revenue_data[community_id]['start_date'] = revenue[0].get('start_date') if len(transactions) else None

    return revenue_data


def create_settlement_instance():

    revenue_data = get_revenue_for_communities()
    epoch_31_dec_2021 = 1640932199000

    for community_id in revenue_data:
        settlement_data = {
            'settlement_id': 'mig_{}'.format(uuid.uuid4()),
            'community_id': community_id,
            'start_epoch': revenue_data[community_id]['start_date'],
            'end_epoch': epoch_31_dec_2021,
            'amount': revenue_data[community_id]['revenue'] * (95/100),
            'fee_amount': revenue_data[community_id]['revenue'] * (5/100),
            'fee_percentage': 5,
            'revenue': revenue_data[community_id]['revenue'],
            'currency': 'INR',
            'status': 2     # processed
        }

        if settlement_data['revenue'] and settlement_data['start_epoch']:
            settlement_serializer = SettlementSerializer(data=settlement_data)

            if settlement_serializer.is_valid():
                print('{}: success'.format(community_id))
                print(settlement_data)

                settlement_instance = settlement_serializer.save()

                transactions = ModelUtilities.get_model_filter(
                    Transaction, {'plan_id__in': revenue_data[community_id]['valid_plan_ids']})

                for transaction in transactions:
                    transaction.settlement_id = settlement_instance.settlement_id

                    if transaction.status == 'refund':
                        transaction.refund_handled = 1

                    transaction.save()

            else:
                print('{}: validation error'.format(community_id))
                print(settlement_serializer.errors)

        else:
            print('{}: data error'.format(community_id))
            print(settlement_data)
