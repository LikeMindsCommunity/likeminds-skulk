from subscription.member_notifications.constants import EVENTS
from subscription.subscriptions.models import Subscription
from subscription.member_notifications.models import MemberNotification
from subscription.utility.time_utilities import TimeUtilities
from subscription.utility.number_utilities import NumberUtilities
from subscription.utility.core_service_utilities import CoreServiceUtilities
import analytics


def send_event(user_id, community_id, event, subscription):

    notification_instance = MemberNotification.get_membership_notification_or_None(user_id=user_id,
                                                                                   community_id=community_id,
                                                                                   code=event['code'])
    if notification_instance is None:

        community_data = CoreServiceUtilities.get_community_data(community_id)

        event_data = {
            'user_id': user_id,
            'community_id': community_id,
            'community_name': '',
            'plan_name': '',
            'amount': 0,
            'end_date': TimeUtilities.convert_epoch_to_date(subscription.valid_till),
            'type': subscription.type
        }

        if community_data is not None:
            event_data['community_name'] = community_data['community']['name']

        transaction_instance = subscription.transaction

        if transaction_instance is not None:
            event_data['plan_name'] = transaction_instance.plan_name
            event_data['amount'] = NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount)

        analytics.track(user_id, event['event'], event_data)

        data = {
            'user_id': user_id,
            'community_id': community_id,
            'code': event['code']
        }

        MemberNotification.create_instance(data)


def handle_renewal_due(subscription):
    send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_DUE'], subscription)


def handle_grace_period_start(subscription):
    if subscription.transaction is not None and subscription.transaction.grace_period > 0:
        send_event(subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_STARTED'], subscription)

    send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_ENDED'], subscription)


def handle_grace_period_end(subscription):
    send_event(subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_ENDED'], subscription)
    send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_ENDED'], subscription)


def handle():

    current_time = TimeUtilities.current_time_in_milliseconds()
    subscriptions = Subscription.objects.filter(is_removed=False)

    for subscription in subscriptions:

        valid_till_with_grace_period = subscription.valid_till

        if subscription.transaction is not None:

            valid_till_with_grace_period = TimeUtilities.add_milliseconds_in_epoch_time(
                subscription.valid_till, subscription.transaction.grace_period)

        if current_time >= valid_till_with_grace_period:
            handle_grace_period_end(subscription)

        elif current_time >= subscription.valid_till:
            handle_grace_period_start(subscription)

        elif current_time >= subscription.renewal_due:
            handle_renewal_due(subscription)
