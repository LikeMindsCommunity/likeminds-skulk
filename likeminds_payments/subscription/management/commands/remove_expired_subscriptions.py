from django.core.management.base import BaseCommand, CommandError
from subscription.subscriptions.models import Subscription
from subscription.utility.time_utilities import TimeUtilities
from subscription.utility.core_service_utilities import CoreServiceUtilities


class Command(BaseCommand):
    help = 'remove all the users whose subscriptions expires'

    def handle(self, *args, **options):

        current_time = TimeUtilities.current_time_in_milliseconds()
        subscriptions = Subscription.objects.all()

        for subscription in subscriptions:

            valid_till_grace_period = subscription.valid_till

            if subscription.transaction is not None:

                valid_till_grace_period = TimeUtilities.add_milliseconds_in_epoch_time(
                    subscription.valid_till, subscription.transaction.grace_period)

            if current_time > valid_till_grace_period:

                response = CoreServiceUtilities.remove_member(subscription.community_id, subscription.user_id)

                if 'error_message' in response:

                    print({'error_message': response['error_message']})
