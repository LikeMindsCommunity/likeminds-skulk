from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.subscriptions.models import Subscription
from subscription.subscription_histories.models import SubscriptionHistory
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.time_utilities import TimeUtilities
import time
import pandas as pd


def get_free_communities():

    # query to fetch free communities
    # select id from togther_community where is_paid=false and created_at<1639756659023;
    # where the time stamp is of date Fri Dec 17 2021 21:27:39
    # the data from above query was exported to a csv file and renamed to free_communities.csv

    input_csv_path = r'./scripts/scripts_data/free_communities.csv'
    df = pd.read_csv(input_csv_path)

    csv_data = {
        'community_ids': df['id']
    }

    free_communities = list(csv_data.get('community_ids'))

    return free_communities


def get_all_members(community_id, member_id):
    members = []
    page = 1
    done = False

    while not done:

        get_members = CoreServiceUtilities.get_all_members(community_id, member_id, page)

        if 'error_message' in get_members:
            done = True
            continue

        if len(get_members['members']) == 0:
            done = True

        for member in get_members['members']:
            members.append(member['id'])

        page += 1

    return members


def generate_data_for_free_subscription(user_id: int, community_id: int, date_subscribed: int) -> dict:
    current_time = TimeUtilities.current_time_in_milliseconds()
    date_subscribed = current_time if date_subscribed == 0 else date_subscribed

    data = {
        "subscription_data": {
            "user_id": user_id,
            "community_id": community_id,
            "plan_id": None,
            "date_subscribed": date_subscribed,
            "valid_till": 1924972199000,
            "date_unsubscribed": None,
            "type": "free",
            "transaction": None
        }
    }

    data["subscription_data"]["renewal_due"] = TimeUtilities.subtract_days_in_epoch_time(
        data["subscription_data"]["valid_till"], 3)

    data["subscription_history_data"] = {
        "start_date": date_subscribed,
        "end_date": data["subscription_data"]["valid_till"],
        "description": 'free subscription',
        "transaction": None,
        "type": "free",
        "user_id": user_id,
        "community_id": community_id
    }

    return data


def generate_new_free_lifetime_subscription(user_id, community_id):

    subscription_instance = Subscription.get_subscription_or_None(user_id, community_id)

    if subscription_instance is None:
        data = generate_data_for_free_subscription(user_id, community_id, 0)

        subscription_instance = Subscription.create_instance(data['subscription_data'])
        subscription_history_instance = SubscriptionHistory.create_instance(
            data['subscription_history_data'])

        if not subscription_instance:
            return {'error_message': 'error creating subscription'}

        if not subscription_history_instance:
            return {'error_message': 'error creating subscription history'}

        return {'success': True}


def main():

    free_communities = get_free_communities()

    all_members = {}
    all_subscriptions = {}
    missing_members = {}
    count = 0

    for community_id in free_communities:
        community_members_data = get_all_members(community_id, 792)
        all_members[community_id] = community_members_data

        all_subscriptions[community_id] = list(ModelUtilities.get_model_filter(
            Subscription, {'community_id': community_id}).values_list('user_id', flat=True))

        missing_members[community_id] = set(all_members[community_id]) - set(all_subscriptions[community_id])

        if len(missing_members[community_id]):
            count += len(missing_members[community_id])
            print('{}({}): {}'.format(community_id, len(missing_members[community_id]), missing_members[community_id]))

        for member in missing_members[community_id]:
            generate_new_free_lifetime_subscription(member, community_id)
            time.sleep(10)

