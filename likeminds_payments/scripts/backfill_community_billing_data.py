import time

import pandas as pd

from subscription.utility.states import TierTypes
from subscription.plans.models import BillingPlan
from subscription.utility.model_utilities import ModelUtilities

def get_all_communities():

    # query to fetch all communities
    # select community_id from collabmates_api_sdkclient order by community_id asc;
    # the data from above query was exported to a csv file and renamed to communities_list.csv

    input_csv_path = r'./scripts/scripts_data/communities_list.csv'
    df = pd.read_csv(input_csv_path)

    csv_data = {
        'community_ids': df['community_id']
    }

    community_list = list(csv_data.get('community_ids'))

    return community_list

def create_billing_plan_for_community_id():
    community_list = get_all_communities()

    for community_id in community_list:
        community_billing_plan = ModelUtilities.get_model_filter(BillingPlan, {'community_id': community_id}).first()

        if community_billing_plan:
            continue
        
        billing_plan_instance = BillingPlan(community_id=community_id, tier_type=TierTypes.FREE.value)
        billing_plan_instance.save()

        print("Success | Community Billing Plan Added", community_id)


print(">>>>>>>>>>>>>>>>>>>>")

start_time = time.time()
create_billing_plan_for_community_id()
end_time = time.time()
print(end_time - start_time)

print(">>>>>>>>>>>>>>>>>>>>")
