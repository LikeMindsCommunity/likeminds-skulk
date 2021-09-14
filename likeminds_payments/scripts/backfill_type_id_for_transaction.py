import time

from subscription.plans.models import SubscriptionEventPlan, SubscriptionPlan
from subscription.transactions.models import Transaction
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.states import TransactionType


def update_community_id_for_community_transaction():
    transaction_filter = ModelUtilities.get_model_filter(Transaction, {'type': TransactionType.COMMUNITY_SUBSCRIPTION})

    for transaction_instance in transaction_filter:

        if transaction_instance.type_id == 0:
            plan_instance = SubscriptionPlan.get_plan_or_None(transaction_instance.plan_id)

            if not plan_instance:
                continue

            transaction_instance.type_id = plan_instance.community_id
            transaction_instance.save()
            print("Success | Community Transaction | payment_id = ", transaction_instance.payment_id)


def update_chatroom_id_for_event_transaction():
    transaction_filter = ModelUtilities.get_model_filter(Transaction, {'type': TransactionType.EVENT})

    for transaction_instance in transaction_filter:

        if transaction_instance.type_id == 0:
            plan_instance = SubscriptionEventPlan.get_event_plan_or_None(transaction_instance.plan_id)

            if not plan_instance:
                continue

            transaction_instance.type_id = plan_instance.chatroom_id
            transaction_instance.save()
            print("Success | Event Transaction | payment_id = ", transaction_instance.payment_id)


print(">>>>>>>>>>>>>>>>>>>>")

start_time = time.time()
update_community_id_for_community_transaction()
update_chatroom_id_for_event_transaction()
end_time = time.time()
print(end_time - start_time)

print(">>>>>>>>>>>>>>>>>>>>")
