from django.core.management.base import BaseCommand, CommandError
import subscription.member_notifications.constants as constants
from subscription.subscriptions.models import Subscription
from subscription.member_notifications.models import MemberNotification
from subscription.utility.time_utilities import TimeUtilities
import analytics


class Command(BaseCommand):
    help = 'remove all the users whose subscriptions expires'

    @staticmethod
    def send_event(user_id, community_id, code):

        notification_instance = MemberNotification.get_membership_notification_or_None(user_id=user_id,
                                                                                       community_id=community_id,
                                                                                       code=code)
        if notification_instance is None:

            # TODO
            # send the segment event

            MemberNotification.create_instance(user_id=user_id, community_id=community_id, code=code)

    def handle(self, *args, **options):

        current_time = TimeUtilities.current_time_in_milliseconds()
        subscriptions = Subscription.objects.all()

        for subscription in subscriptions:

            valid_till_with_grace_period = subscription.valid_till

            if subscription.transaction is not None:

                valid_till_with_grace_period = TimeUtilities.add_milliseconds_in_epoch_time(
                    subscription.valid_till, subscription.transaction.grace_period)

            if current_time >= subscription.renewal_due:

                self.send_event(subscription.user_id, subscription.community_id, constants.SUBSCRIPTION_DUE)

            if current_time >= subscription.valid_till:

                if subscription.transaction is not None and subscription.transaction.grace_period > 0:
                    self.send_event(subscription.user_id, subscription.community_id, constants.GRACE_PERIOD_STARTED)

                self.send_event(subscription.user_id, subscription.community_id, constants. SUBSCRIPTION_ENDED)

            if current_time >= valid_till_with_grace_period:

                self.send_event(subscription.user_id, subscription.community_id, constants.GRACE_PERIOD_ENDED)
                self.send_event(subscription.user_id, subscription.community_id, constants.SUBSCRIPTION_ENDED)
