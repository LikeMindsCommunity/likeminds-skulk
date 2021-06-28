import pandas as pd
from subscription.plans.models import SubscriptionPlan
from subscription.transactions.models import Transaction
from subscription.subscriptions.models import Subscription
from subscription.subscription_histories.models import SubscriptionHistory
from subscription.utility.time_utilities import TimeUtilities

transaction_data = pd.read_excel(r'scripts/plans/plan.xlsx', sheet_name="Transaction data")
df = pd.DataFrame(transaction_data, columns=['payment_id', 'email', 'amount', 'currency', 'status', 'method', 'contact',
                                             'created_at','Community Name', 'plan_name', 'Community_id', 'Users',
                                             'plan_duration', 'payment_page_url'])

t_user_id = df['Users']
t_community_id = df['Community_id']
t_payment_id = df['payment_id']


def find_transaction(user_id, community_id):

    output = []

    for i in range(len(t_user_id)):

        if isinstance(t_user_id[i], int):
            if t_user_id[i] == user_id and t_community_id[i] == community_id:
                output.append(t_payment_id[i])

    return output


def generate_subscriptions():

    data = pd.read_excel(r'./scripts/plans/plan.xlsx', sheet_name="All community members")
    df = pd.DataFrame(data,
                      columns=['community_id_id', 'member_id_id', 'became_member_at', 'state', 'is_owner', 'name',
                               'exempt'])

    community_id = df['community_id_id']
    member_id = df['member_id_id']
    became_member_at = df['became_member_at']
    state = df['state']
    is_owner = df['is_owner']
    name = df['name']
    exempt = df['exempt']

    count = 1

    for i in range(len(member_id)):

        subscription = Subscription.objects.filter(user_id=member_id[i], community_id=community_id[i])

        if len(subscription) == 0:

            transaction_list = find_transaction(member_id[i], community_id[i])

            if len(transaction_list) == 0:

                if state[i] == 1 or exempt[i] == 'TRUE':

                    instance = Subscription()
                    instance.user_id = member_id[i]
                    instance.community_id = community_id[i]
                    instance.plan_id = None
                    instance.date_subscribed = became_member_at[i]
                    instance.valid_till = 1924972199000
                    instance.date_unsubscribed = None
                    instance.type = 'free'
                    instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(1924972199000, 3)
                    instance.transaction = None
                    instance.save()

                    instance2 = SubscriptionHistory()
                    instance2.start_date = instance.date_subscribed
                    instance2.end_date = instance.valid_till
                    instance2.description = 'free subscription'
                    instance2.transaction = None
                    instance2.type = 'free'
                    instance2.user_id = instance.user_id
                    instance2.community_id = instance.community_id
                    instance2.save()

                else:

                    instance = Subscription()
                    instance.user_id = member_id[i]
                    instance.community_id = community_id[i]
                    instance.plan_id = None
                    instance.date_subscribed = became_member_at[i]
                    instance.valid_till = 1625183940
                    instance.date_unsubscribed = None
                    instance.type = 'free'
                    instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(1625183940, 3)
                    instance.transaction = None
                    instance.save()

                    instance2 = SubscriptionHistory()
                    instance2.start_date = instance.date_subscribed
                    instance2.end_date = instance.valid_till
                    instance2.description = 'free subscription'
                    instance2.transaction = None
                    instance2.type = 'free'
                    instance2.user_id = instance.user_id
                    instance2.community_id = instance.community_id
                    instance2.save()


            else:

                for transaction in transaction_list:

                    transaction_instance = Transaction.objects.get(payment_id=transaction)

                    plan_instance = SubscriptionPlan.objects.get(plan_id=transaction_instance.plan_id)

                    subscription_instance = Subscription.objects.filter(user_id=member_id[i],
                                                                        community_id=community_id[i])

                    if len(subscription_instance) == 0:

                        instance = Subscription()
                        instance.user_id = member_id[i]
                        instance.community_id = community_id[i]
                        instance.plan_id = transaction_instance.plan_id
                        instance.date_subscribed = became_member_at[i]
                        instance.valid_till = TimeUtilities.add_months_in_epoch_time(became_member_at[i], plan_instance.duration_in_months)
                        instance.date_unsubscribed = None
                        instance.type = 'onetime'
                        instance.renewal_due = TimeUtilities.subtract_days_in_epoch_time(instance.valid_till, 3)
                        instance.transaction = transaction_instance
                        instance.save()


                        instance2 = SubscriptionHistory()
                        instance2.start_date = instance.date_subscribed
                        instance2.end_date = instance.valid_till
                        instance2.description = 'paid subscription'
                        instance2.transaction = transaction_instance
                        instance2.type = 'paid'
                        instance2.user_id = instance.user_id
                        instance2.community_id = instance.community_id
                        instance2.save()

                    else:

                        current_time = TimeUtilities.current_time_in_milliseconds()

                        instance = subscription_instance[0]
                        instance.plan_id = transaction_instance.plan_id
                        instance.type = 'onetime'

                        if instance.valid_till > current_time:
                            instance.valid_till = TimeUtilities.add_months_in_epoch_time(instance.valid_till, plan_instance.duration_in_months)
                        else:
                            instance.valid_till = TimeUtilities.add_months_in_epoch_time(current_time, plan_instance.duration_in_months)

                        instance.save()

                        instance2 = SubscriptionHistory()
                        instance2.start_date = instance.date_subscribed
                        instance2.end_date = instance.valid_till
                        instance2.description = 'paid transaction'
                        instance2.transaction = transaction_instance
                        instance2.type = 'paid'
                        instance2.user_id = instance.user_id
                        instance2.community_id = instance.community_id
                        instance2.save()

        print(count)
        count += 1


if __name__ == "__main__":
    generate_subscriptions()