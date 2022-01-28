from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.subscriptions.models import Subscription
from subscription.utility.model_utilities import ModelUtilities

import pandas as pd
import time


def get_removed_members():

    """query to fetch members who are not renewed

    select
    distinct nt.community_id, nt.member_id
    from
    (select
    rm.community_id, rm.member_id
    from togther_removedmembers rm
    left join togther_members cm
    on cm.member_id_id = rm.member_id and cm.community_id_id = rm.community_id
    where (cm.member_id_id is null or cm.community_id_id is null) and rm.removed_state = 2) nt
    left join togther_subscriptionexpiredmembers em
    on nt.community_id = em.community_id and nt.member_id = em.member_id
    where em.community_id is not null and em.member_id is not null; """

    input_csv_path = r'./scripts/scripts_data/renew_member.csv'
    df = pd.read_csv(input_csv_path)

    csv_data = {
        'community_ids': df['community_id'],
        'member_ids': df['member_id']
    }

    return csv_data


def main():

    removed_members = get_removed_members()

    for i in range(len(removed_members['member_ids'])):

        subscription_records = ModelUtilities.get_model_filter(
            Subscription, {'user_id': removed_members['member_ids'][i],
                           'community_id': removed_members['community_ids'][i]})

        if not subscription_records:
            continue

        subscription = subscription_records[0]

        print(subscription.user_id, subscription.community_id, subscription.is_removed)

        if subscription.is_removed:

            response = CoreServiceUtilities.renew_member(subscription.community_id, subscription.user_id)
            print(response)

            if 'success' in response and response['success']:
                subscription.is_removed = False
                subscription.save()
                print('success', subscription.community_id, subscription.user_id)

            time.sleep(2)




