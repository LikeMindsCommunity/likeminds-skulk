from django.core.management.base import BaseCommand
from subscription.member_notifications.constants import EVENTS
from subscription.subscriptions.models import Subscription
from subscription.member_notifications.models import MemberNotification
from subscription.utility.time_utilities import TimeUtilities
import analytics


class Command(BaseCommand):
    help = 'send events to users based on their membership state'

    @staticmethod
    def check_existence(user_id, community_id, code):

        notification_instance = MemberNotification.get_membership_notification_or_None(user_id=user_id,
                                                                                       community_id=community_id,
                                                                                       code=code)
        if notification_instance is None:
            return False
        return True

    @staticmethod
    def send_event(user_id, community_id, event):

        analytics.track(user_id, event['event'], {
            'user_id': user_id,
            'community_id': community_id
        })

        MemberNotification.create_instance(user_id=user_id, community_id=community_id, code=event['code'])

    def handle(self, *args, **options):

        current_time = TimeUtilities.current_time_in_milliseconds()
        subscriptions = Subscription.objects.filter(is_removed=False)

        for subscription in subscriptions:

            valid_till_with_grace_period = subscription.valid_till

            if subscription.transaction is not None:

                valid_till_with_grace_period = TimeUtilities.add_milliseconds_in_epoch_time(
                    subscription.valid_till, subscription.transaction.grace_period)

            if current_time >= subscription.renewal_due and not self.check_existence(
                    subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_DUE']['code']):
                self.send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_DUE'])

            elif current_time >= subscription.valid_till:

                if subscription.transaction is not None:

                    if subscription.transaction.grace_period > 0 and not self.check_existence(
                            subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_STARTED']['code']):
                        self.send_event(subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_STARTED'])

                if not self.check_existence(subscription.user_id, subscription.community_id,
                                            EVENTS['SUBSCRIPTION_ENDED']['code']):
                    self.send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_ENDED'])

            elif current_time >= valid_till_with_grace_period:

                if not self.check_existence(subscription.user_id, subscription.community_id,
                                            EVENTS['GRACE_PERIOD_ENDED']['code']):
                    self.send_event(subscription.user_id, subscription.community_id, EVENTS['GRACE_PERIOD_ENDED'])

                if not self.check_existence(subscription.user_id, subscription.community_id,
                                            EVENTS['SUBSCRIPTION_ENDED']['code']):
                    self.send_event(subscription.user_id, subscription.community_id, EVENTS['SUBSCRIPTION_ENDED'])
