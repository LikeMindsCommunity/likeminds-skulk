from subscription.plans.models import SubscriptionPlan
from subscription.transactions.models import Transaction
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.external_services.s3.s3_wrapper import S3Wrapper
from django.conf import settings
import pandas as pd
import uuid
import time
from datetime import datetime
from io import StringIO


def generate_transactions(input_file_path: str = r'./scripts/members_data.csv'):
    print('script process started')

    input_csv_path = input_file_path

    print('reading csv data from: {}'.format(input_csv_path))

    data = get_csv_data(input_csv_path)
    print('got data from csv')

    output_csv_name = '{}_otl_data_{}.csv'.format(data['community_id'][0], datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))

    row_count = len(data['member_email'])
    print('number of transactions to create: {}'.format(row_count))

    final_lists_dict = process_csv_data(row_count, data)
    output_data = create_output_data(final_lists_dict)

    print("script process completed")

    upload_file = upload_csv_to_s3(output_data, output_csv_name)

    return upload_file


def get_csv_data(file_path):
    df = pd.read_csv(file_path)

    csv_data = {
        'plan_id': df['plan_id'],
        'member_email': df['member_email'],
        'member_phone': df['member_phone (with country code)'],
        'start_date': df['start_date (dd/mm/yyyy)'],
        'community_id': df['community_id'],
        'payment_page_url': df['payment_page_url'],
        'amount': df['amount'],
        'community_name': df['community_name']
    }

    return csv_data


def process_csv_data(count, data):
    final_lists_dict = {
        'phones': [],
        'emails': [],
        'otls': [],
        'community_names': [],
        'payment_ids': [],
        'plan_ids': []
    }

    if count == 0:
        return final_lists_dict

    loop_over_data_and_create_transactions(count, data, final_lists_dict)

    return final_lists_dict


def loop_over_data_and_create_transactions(count, data, final_lists_dict):

    for i in range(count):

        user_phone = '+' + str(data['member_phone'][i])
        user_email = data['member_email'][i]
        community_name = data['community_name'][i]
        plan_id = data['plan_id'][i]
        payment_id = 'mig_{}'.format(uuid.uuid4())

        plan_instance = SubscriptionPlan.get_plan_or_None(plan_id=plan_id)

        if plan_instance is None:
            add_to_lists(final_lists_dict, user_phone, user_email, None, community_name, payment_id, plan_id)
            continue

        community_data = CoreServiceUtilities.get_community_data(plan_instance.community_id)

        transaction_object = create_transaction_object(plan_instance, community_data, payment_id, user_phone, data, i)
        create_transaction_instance(transaction_object)

        print("{}: transaction with id: {} created".format(i, payment_id))
        time.sleep(0.01)  # 10 ms delay time

        otl_url = CoreServiceUtilities.fetch_otl_url(community_id=data['community_id'][i],
                                                     payment_id=transaction_object['payment_id'])

        if 'error_message' in otl_url:
            add_to_lists(final_lists_dict, user_phone, user_email, None, community_name, payment_id, plan_id)

        else:
            add_to_lists(final_lists_dict, user_phone, user_email, otl_url['private_link'], community_name, payment_id,
                         plan_id)


def add_to_lists(lists_dict, user_phone, user_email, otl, community_name, payment_id, plan_id):
    lists_dict['phones'].append(user_phone)
    lists_dict['emails'].append(user_email)
    lists_dict['otls'].append(otl)
    lists_dict['community_names'].append(community_name)
    lists_dict['payment_ids'].append(payment_id)
    lists_dict['plan_ids'].append(plan_id)


def create_transaction_object(plan_instance, community_data, payment_id, user_phone, data, iterator):
    transaction_timestamp = int(datetime.strptime(str(data['start_date'][iterator]), "%d/%m/%Y").timestamp() * 1000)
    amount = data['amount'][iterator] * 100,

    transaction = {
        "plan_id": plan_instance.plan_id,
        "payment_id": payment_id,
        "community_name": community_data['community']['name'],
        "plan_name": plan_instance.name,
        "plan_cost": plan_instance.cost,
        "renew": False,
        "amount": amount[0],
        "payment_email": data['member_email'][iterator],
        "payment_phone": user_phone,
        "currency": "INR",
        "is_international": False,
        "method": "migration",
        "status": "captured",
        "error_description": '',
        "refund_amount": 0,
        "user_id": None,
        "payment_page_url": data['payment_page_url'][iterator],
        "shared_by": None,
        "grace_period": 0,
        "created_at": transaction_timestamp,
        "updated_at": transaction_timestamp
    }

    return transaction


def create_transaction_instance(transaction):
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


def create_output_data(final_lists_dict):
    data = pd.DataFrame({
        'phone': final_lists_dict['phones'],
        'email': final_lists_dict['emails'],
        'otl': final_lists_dict['otls'],
        'community_name': final_lists_dict['community_names'],
        'payment_id': final_lists_dict['payment_ids'],
        'plan_id': final_lists_dict['plan_ids']
    })

    return data


def write_data_to_file(data, file_path):
    data.to_csv(file_path, index=False)


def upload_csv_to_s3(data, file_name):
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)

    file_path = 'utilities/otl_files/{}'.format(file_name)
    bucket = settings.S3_BUCKETS.get('media_bucket').get('name')

    upload_status = S3Wrapper.upload_csv_file(file_path, bucket, csv_buffer, acl='public-read')

    if upload_status:
        return {'link': 'https://{}.s3.amazonaws.com/{}'.format(bucket, file_path)}

    return {'error_message': 'error while uploading csv file'}
