from subscription.plans.models import SubscriptionPlan
from subscription.transactions.models import Transaction
from subscription.utility.core_service_utilities import CoreServiceUtilities
import pandas as pd
import uuid
from datetime import datetime


def generate_transactions():
    df = pd.read_csv(r'./scripts/members_data.csv')

    plan_name = df['plan_name']
    plan_duration = df['plan_duration(in months)']
    member_email = df['member_email']
    member_phone = df['member_phone (with country code)']
    start_date = df['start_date (dd/mm/yyyy)']
    community_id = df['community_id']
    # payment_page_url = df['payment_page_url']
    amount = df['amount']

    phones = []
    emails = []
    otls = []

    for i in range(len(member_email)):

        user_phone = "+" + str(member_phone[i])

        payment_id = "mig_{}".format(uuid.uuid4())
        plan_instances = SubscriptionPlan.objects.filter(community_id=community_id[i],
                                                         duration_in_months=plan_duration[i],
                                                         name=plan_name[i])
        if len(plan_instances) == 0:
            phones.append(user_phone)
            emails.append(member_email[i])
            otls.append(None)
            continue

        plan_instance = plan_instances[0]
        community_data = CoreServiceUtilities.get_community_data(plan_instance.community_id)

        current_time = int(datetime.strptime(str(start_date[i]), "%d/%m/%Y").timestamp() * 1000)

        transaction = {
            "plan_id": plan_instance.plan_id,
            "payment_id": payment_id,
            "community_name": community_data['community']['name'],
            "plan_name": plan_instance.name,
            "plan_cost": plan_instance.cost,
            "renew": False,
            "amount": amount[i] * 100,
            "payment_email": member_email[i],
            "payment_phone": user_phone,
            "currency": "INR",
            "is_international": False,
            "method": "migration",
            "status": "captured",
            "error_description": '',
            "refund_amount": 0,
            "user_id": None,
            "payment_page_url": 'payment_page_url[i]',
            "shared_by": None,
            "grace_period": 0,
            "created_at": current_time,
            "updated_at": current_time
        }

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

        otl_url = CoreServiceUtilities.fetch_otl_url(community_id=community_id[i], payment_id=transaction['payment_id'])

        if 'error_message' in otl_url:
            phones.append(user_phone)
            emails.append(member_email[i])
            otls.append(None)

        else:
            phones.append(user_phone)
            emails.append(member_email[i])
            otls.append(otl_url['private_link'])

    final_data = pd.DataFrame({'phone': phones, 'email': emails, 'otl': otls})
    file_name = 'otl_data_{}.csv'.format(datetime.today().strftime('%Y-%m-%d'))
    final_data.to_csv(file_name, index=False)
