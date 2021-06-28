from subscription.plans.models import SubscriptionPlan
import time
import psycopg2
import pandas as pd


def generate_data():

    data = pd.read_excel(r'./scripts/plans/plan.xlsx', sheet_name="All plan data")
    df = pd.DataFrame(data,
                      columns=['Plan_id', 'Community_name', 'Community_id', 'Plan Name', 'cost', 'Plan_duration',
                               'public link', 'cm_email', 'cb_email', 'plan_name', 'currency', 'usd', 'status'])

    planId = df['Plan_id']
    communityName = df['Community_name']
    communityId = df['Community_id']
    planName = df['Plan Name']
    planCost = df['cost']
    planDuration = df['Plan_duration']
    joinLink = df['public link']
    cmMail = df['cm_email'].fillna('')
    cbMail = df['cb_email'].fillna('')
    planDisplayName = df['plan_name'].fillna('')
    default_currency = df['currency']
    cost_usd = df['usd']
    status = df['status']

    values = {
        'Monthly Membership': 'monthly',
        'Monthly membership': 'monthly',
        'Quarterly Membership': 'quarterly',
        'Quarterly membership': 'quarterly',
        'Half Yearly Membership': 'half_yearly',
        'Yearly Membership': 'yearly',
        'Lifetime Membership': 'lifetime'
    }

    PLAN_IMAGES = {
        "monthly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a772ddb19c5_Price%20Icon%2001.svg",
        "quarterly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a251adb19c6_Price%20Icon%2002.svg",
        "half_yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
        "yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
        "lifetime": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg"
    }

    # con = psycopg2.connect(database="lmpaymentdb", user="postgres", password="TheLikeMinds!1990",
    #                        host="payment-beta.cgx3gr7xnezq.ap-south-1.rds.amazonaws.com", port="5432")
    # print("Database opened successfully")
    # cur = con.cursor()
    count = 1
    for i in range(len(planId)):
        current_time = int(time.time() * 1000)

        if status[i] != 'Active':
            continue
        plan = {
            "id": count,
            "plan_id": planId[i],
            "community_id": communityId[i],
            "name": planDisplayName[i],
            "duration_name": values[planName[i]],
            "cost": int(planCost[i])*100,
            "strike_cost": None,
            "cost_usd": None if cost_usd[i] == 0 else int(cost_usd[i]),
            "strike_cost_usd": None,
            "duration_in_months": planDuration[i],
            "cm_emails": cmMail[i],
            "buddy_emails": cbMail[i],
            "is_deleted": False,
            "description": '',
            "referral_free_days": 0,
            "image": PLAN_IMAGES[values[planName[i]]],
            "created_at": current_time,
            "updated_at": current_time
        }
        instance = SubscriptionPlan()
        instance.plan_id = plan['plan_id']
        instance.community_id = plan['community_id']
        instance.name = plan['name']
        instance.duration_name = plan['duration_name']
        instance.cost = plan['cost']
        instance.strike_cost = plan['strike_cost']
        instance.cost_usd = plan['cost_usd']
        instance.strike_cost_usd = plan['strike_cost_usd']
        instance.duration_in_months = plan['duration_in_months']
        instance.cm_emails = plan['cm_emails']
        instance.buddy_emails = plan['buddy_emails']
        instance.is_deleted = False
        instance.description = plan['description']
        instance.referral_free_days = plan['referral_free_days']
        instance.image = plan['image']
        instance.created_at = plan['created_at']
        instance.updated_at = plan['updated_at']
        instance.save(using="test")
        print(count)
        count += 1


if __name__ == "__main__":
    generate_data()
