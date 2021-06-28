from subscription.plans.models import SubscriptionPlan
from subscription.transactions.models import Transaction
import pandas as pd
import time
import uuid
from datetime import datetime


def generate_transactions():

    data = pd.read_excel(r'./scripts/plans/plan.xlsx', sheet_name='Transaction data')
    df = pd.DataFrame(data,
                      columns=['payment_id', 'email', 'amount', 'currency', 'status', 'method', 'contact', 'created_at',
                               'Community Name', 'plan_name', 'Community_id', 'Users', 'plan_duration', 'payment_page_url'])

    paymentId = df['payment_id']
    email = df['email']
    amount = df['amount']
    currency = df['currency']
    status = df['status']
    method = df['method']
    contact = df['contact']
    created_at = df['created_at']
    communityName = df['Community Name']
    planName = df['plan_name']
    communityId = df['Community_id']
    updatedUserIds = df['Users']
    planDuration = df['plan_duration']
    paymentPageUrl = df['payment_page_url']

    PLAN_IMAGES = {
        "monthly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a772ddb19c5_Price%20Icon%2001.svg",
        "quarterly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a251adb19c6_Price%20Icon%2002.svg",
        "half_yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
        "yearly": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg",
        "lifetime": "https://global-uploads.webflow.com/605033ad58253a624fdb1964/605033ad58253a9534db19c7_Price%20Icon%2003.svg"
    }

    values = {
        ' Yearly Plan': 'yearly',
        'Yearly Plan': 'yearly',
        12: 'yearly',
        'Half Yearly Plan': 'half_yearly',
        ' half yearly plan': 'half_yearly',
        ' Half Yearly Plan': 'half_yearly',
        'half yearly plan': 'half_yearly',
        6: 'half_yearly',
        ' Quarterly Plan Plan': 'quarterly',
        'Quarterly Plan Plan': 'quarterly',
        ' Quarterly Plan': 'quarterly',
        'Quarterly Plan': 'quarterly',
        ' Quarterly plan': 'quarterly',
        'Quarterly plan': 'quarterly',
        3: 'quarterly',
        ' Monthly Plan': 'monthly',
        'Monthly Plan': 'monthly',
        'Monthly plan': 'monthly',
        ' Monthly plan': 'monthly',
        1: 'monthly'
    }

    plan_values = {
        'Half Yearly Plan': 6,
        'half yearly plan': 6,
        'Monthly Plan': 1,
        'Monthly plan': 1,
        'Quarterly Plan': 3,
        'Quarterly Plan Plan': 3,
        'Quarterly plan': 3,
        'Yearly Plan': 12
    }

    count = 1
    for i in range(len(paymentId)):

        print(communityId[i], values[planDuration[i]], updatedUserIds[i])
        plans = SubscriptionPlan.objects.filter(
            community_id=communityId[i], duration_name=values[planDuration[i]])
        if len(plans) == 0:
            current_time = int(time.time())*1000

            instance = SubscriptionPlan()
            instance.plan_id = str(uuid.uuid4())
            instance.community_id = communityId[i]
            instance.name = ''
            instance.duration_name = values[planDuration[i]]
            instance.cost = amount[i]*100
            instance.strike_cost = None
            instance.cost_usd = None
            instance.strike_cost_usd = None
            instance.duration_in_months = planDuration[i] if isinstance(planDuration[i], int) else plan_values[planDuration[i]]
            instance.cm_emails = 'mahir.gupta@likeminds.community'
            instance.buddy_emails = 'himanshu.saleria@likeminds.community'
            instance.is_deleted = True
            instance.description = ''
            instance.referral_free_days = 0
            instance.image = PLAN_IMAGES[values[planDuration[i]]]
            instance.created_at = current_time
            instance.updated_at = current_time
            instance.save()

            plans = SubscriptionPlan.objects.filter(
                community_id=communityId[i], duration_name=values[planDuration[i]])
        plan = plans.last()

        try:
            current_time = int(datetime.strptime(str(created_at[i]), "%Y-%m-%d %H:%M:%S").timestamp()*1000)
        except:
            try:
                current_time = int(datetime.strptime(str(created_at[i]), "%m/%d/%Y %H:%M %p").timestamp()*1000)
            except:
                print("error")
                current_time = int(time.time()*100)

        transaction = {
            "plan_id": plan.plan_id,
            "payment_id": paymentId[i],
            "community_name": communityName[i],
            "plan_name": plan.name,
            "plan_cost": plan.cost,
            "renew": False,
            "amount": amount[i]*100,
            "payment_email": email[i],
            "payment_phone": contact[i],
            "currency": currency[i],
            "is_international": False,
            "method": method[i],
            "status": status[i],
            "error_description": '',
            "refund_amount": 0,
            "user_id": updatedUserIds[i] if isinstance(updatedUserIds[i], int) else None,
            "payment_page_url": paymentPageUrl[i],
            "shared_by": None,
            "grace_period": 0,
            "created_at": current_time,
            "updated_at": current_time
        }
        count += 1

        instance = Transaction()
        instance.plan_id = transaction['plan_id']
        instance.payment_id = transaction['payment_id']
        instance.community_name = transaction['community_name']
        instance.plan_name = transaction['plan_name']
        instance.plan_cost = transaction['plan_cost']
        instance.renew = transaction['renew']
        instance.amount = transaction['amount']
        instance.payment_email = transaction['payment_email']
        instance.payment_phone = transaction['payment_phone']
        instance.currency = transaction['currency']
        instance.is_international = transaction['is_international']
        instance.method = transaction['method']
        instance.status = transaction['status']
        instance.error_description = transaction['error_description']
        instance.refund_amount = transaction['refund_amount']
        instance.user_id = transaction['user_id']
        instance.payment_page_url = transaction['payment_page_url']
        instance.shared_by = transaction['shared_by']
        instance.grace_period = transaction['grace_period']
        instance.created_at = transaction['created_at']
        instance.updated_at = transaction['updated_at']
        instance.save()


if __name__ == "__main__":
    generate_transactions()
