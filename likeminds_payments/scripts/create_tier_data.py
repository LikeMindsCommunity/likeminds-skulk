import time

import pandas as pd

from subscription.plans.models import TierPlan
from subscription.utility.model_utilities import ModelUtilities


def get_all_tier_plans():

    import_csv_path = r'./scripts/scripts_data/subscription_tierplan.csv'
    df = pd.read_csv(import_csv_path)

    csv_data = {
        'tier_types': df['tier_type'],
        'tier_limit_types': df['tier_value_type'],
        'max_request_limit_values': df['max_request_limit_value'],
        'ttls': df['ttl'],
        'rate_limit_key_names': df['rate_limit_key_name'],
        'error_messages': df['error_message']
    }

    tier_list = list(zip(csv_data.get('tier_types'), csv_data.get('tier_limit_types'), csv_data.get('max_request_limit_values'), csv_data.get('ttls'), csv_data.get('rate_limit_key_names'), csv_data.get('error_messages')))

    return tier_list

def create_tier_plan():

    tier_plans = get_all_tier_plans()

    for tier_plan_data in tier_plans:
        tier_plan = ModelUtilities.get_model_filter(TierPlan, {'tier_type': tier_plan_data[0]})

        if tier_plan:
            continue
        
        tier_plan_instance = TierPlan(tier_type=tier_plan_data[0], tier_value_type=tier_plan_data[1], max_request_limit_value=tier_plan_data[2], ttl=tier_plan_data[3], rate_limit_key_name=tier_plan_data[4], error_message=tier_plan_data[5])
        tier_plan_instance.save()

        print("Success | Community Billing Plan Added", tier_plan_data[0])

print(">>>>>>>>>>>>>>>>>>>>")

start_time = time.time()
create_tier_plan()
end_time = time.time()
print(end_time - start_time)

print(">>>>>>>>>>>>>>>>>>>>")
