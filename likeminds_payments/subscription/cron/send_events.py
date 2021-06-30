from subscription.member_notifications.constants import EVENTS
from subscription.subscriptions.models import Subscription
from subscription.member_notifications.models import MemberNotification
from subscription.utility.time_utilities import TimeUtilities
import analytics


def send_event(user_id, community_id, event):

    notification_instance = MemberNotification.get_membership_notification_or_None(user_id=user_id,
                                                                                   community_id=community_id,
                                                                                   code=event['code'])
    if notification_instance is None:

        analytics.track(user_id, event['event'], {
            'user_id': user_id,
            'community_id': community_id
        })

        MemberNotification.create_instance(user_id=user_id, community_id=community_id, code=event['code'])


def handle_renewal_due(subscription):
    send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_DUE'])


def handle_grace_period_start(subscription):
    if subscription.transaction is not None and subscription.transaction.grace_period > 0:
        send_event(subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_STARTED'])

    send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_ENDED'])


def handle_grace_period_end(subscription):
    send_event(subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_ENDED'])
    send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_ENDED'])


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
