from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from django.template.loader import get_template
from subscription.external_services.webflow.webflow_impl import WebflowImpl
from subscription.plans.constants import EVENT_PAYMENT_LINK
from subscription.plans.models import SubscriptionEventPlan
from subscription.transactions.models import Transaction
from subscription.payment_page.models import PaymentPageMeta
from subscription.subscriptions.constants import (PAYMENT_SUCCESS_MEMBERSHIP_WHATSAPP_TEMPLATE_NAME,
                                                  PAYMENT_SUCCESS_MEMBERSHIP_WHATSAPP_BROADCAST_NAME,
                                                  PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_CM_SUBJECT,
                                                  PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_MEMBER_SUBJECT,
                                                  PAYMENT_SUCCESS_MEMBERSHIP_RENEW_EMAIL_TO_CM_SUBJECT)
from subscription.payment_page.constants import (PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_MEMBER_BODY,
                                                 PAYMENT_PAGE_PAYMENT_FAILED_EMAIL_TO_MEMBER_BODY,
                                                 PAYMENT_PAGE_PAYMENT_SUCCESS_MEMBER_WHATSAPP_TEMPLATE_NAME,
                                                 PAYMENT_PAGE_PAYMENT_SUCCESS_MEMBER_WHATSAPP_BROADCAST_NAME,
                                                 PAYMENT_PAGE_PAYMENT_FAILED_MEMBER_WHATSAPP_TEMPLATE_NAME,
                                                 PAYMENT_PAGE_PAYMENT_FAILED_MEMBER_WHATSAPP_BROADCAST_NAME,
                                                 PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_CM_BODY)
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.utility.model_utilities import ModelUtilities

from subscription.utility.number_utilities import NumberUtilities
from subscription.utility.string_utilities import StringUtilities


def create_event_meta_for_webflow_update(event_plan_instance):
    event_meta = {
        'fields': {
            'cost': StringUtilities.get_string_from_integer(
                NumberUtilities.convert_to_rupee_or_none(event_plan_instance.strike_cost)),
            'payment-link': EVENT_PAYMENT_LINK % (
                settings.WEB_URL, event_plan_instance.event_plan_id,
                event_plan_instance.chatroom_id, event_plan_instance.community_id)
        }
    }

    return event_meta


@shared_task
def update_event_in_webflow_service(event_plan_id, user_id):
    event_plan_filter = ModelUtilities.get_model_filter(SubscriptionEventPlan,
                                                        {'event_plan_id': event_plan_id})

    if not event_plan_filter:
        return

    event_plan_instance = event_plan_filter[0]
    webflow_item_id = None
    event_meta = create_event_meta_for_webflow_update(event_plan_instance)
    chatroom_meta = CoreServiceUtilities.chatroom_fetch({'chatroom_id': event_plan_instance.chatroom_id,
                                                         'member_id': user_id}).get('chatroom')

    if chatroom_meta and chatroom_meta.get('webflow_item_id'):
        webflow_item_id = chatroom_meta.get('webflow_item_id')

    if not webflow_item_id:
        return

    WebflowImpl.update_event_in_webflow(event_meta, webflow_item_id)


@shared_task
def get_first_verified_email_and_phone(user_id, user_details_object=None):

    email = None
    mobile_no = None
    country_code = None

    if not user_details_object:
        user_details_object = CoreServiceUtilities.get_user_details({"member_id": user_id})

    if 'user' in user_details_object:

        if 'emails' not in user_details_object['user']:
            return {'error_message': 'error while fetching email'}

        else:

            for user_email_object in user_details_object['user']['emails']:

                if user_email_object['verified']:
                    email = user_email_object['email']
                    break

        if 'mobiles' not in user_details_object['user']:
            return {'error_message': 'error while fetching mobile no'}

        else:

            for user_mobile_object in user_details_object['user']['mobiles']:

                if user_mobile_object['state'] == 1:
                    mobile_no = user_mobile_object['mobile_no']
                    country_code = user_mobile_object['country_code']
                    break

    else:
        return {'error_message': 'error while fetching user details'}

    return {'email': email, 'mobile_no': mobile_no, 'country_code': country_code}


@shared_task
def send_email_from_core_service(user_id, email_body):
    send_email_response = CoreServiceUtilities.send_email(user_id, email_body)

    if send_email_response.get('success'):
        return send_email_response

    return {'success': False, 'error_message': 'Some error occured while sending mail'}


@shared_task
def send_wa_messages(user_id, whatsapp_body):
    send_wa_message_response = CoreServiceUtilities.send_wa_messages(user_id, whatsapp_body)

    if send_wa_message_response.get('success'):
        return send_wa_message_response

    return {'success': False, 'error_message': 'Some error occured while sending whatsapp messages'}


@shared_task
def payment_page_member_payment_success_email(transaction_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                          {"payment_page_id": transaction_instance.plan_id})

    if not payment_page_filter:
        return {'error_message': "Invalid plan_id for payment page"}

    payment_page_instance = payment_page_filter[0]

    # Get Owner of community
    community_owner_details = CoreServiceUtilities.get_community_admins(transaction_instance.type_id,
                                                                        fetch_owner_only=True)

    if not community_owner_details:
        return {'error_message': "No owner found for the community"}

    community_owner_details = community_owner_details[0]

    # Community Owner email
    owner_verified_email_and_phone = get_first_verified_email_and_phone(community_owner_details['id'])

    if 'error_message' in owner_verified_email_and_phone:
        return {'error_message': owner_verified_email_and_phone['error_message']}

    successful_payment_message = payment_page_instance.custom_success_message if \
        payment_page_instance.custom_success_message else ""

    member_payment_success_mail_template = get_template(
        'payment_success_member_email_payment_page.html').render(
        {"member_name": transaction_instance.payment_name,
         "currency": transaction_instance.currency,
         "amount": NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount),
         "community_name": transaction_instance.community_name,
         "successful_payment_message": successful_payment_message,
         "community_manager_name": community_owner_details['name']})

    payment_page_mail_body_payment_success_member = PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_MEMBER_BODY.copy()

    payment_page_mail_body_payment_success_member['subject'] = payment_page_mail_body_payment_success_member[
        'subject'].format(transaction_instance.community_name)
    payment_page_mail_body_payment_success_member['mail_body'] = member_payment_success_mail_template
    payment_page_mail_body_payment_success_member['mail_recipient_list'] = [transaction_instance.payment_email]
    payment_page_mail_body_payment_success_member['reply_to'] = [owner_verified_email_and_phone['email']]

    send_email_response = send_email_from_core_service(community_owner_details['id'],
                                                       payment_page_mail_body_payment_success_member)

    payment_success_whatsapp_member_body = {
        "receivers_list": [
            {
                "whatsappNumber": NumberUtilities.get_integer_from_string(transaction_instance.payment_phone),
                "customParams": [
                    {
                        "name": "name",
                        "value": transaction_instance.payment_name
                    },
                    {
                        "name": "amount",
                        "value": str(transaction_instance.currency) + " " +
                                 str(NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount))
                    },
                    {
                        "name": "payment_page_title",
                        "value": payment_page_instance.title
                    },
                    {
                        "name": "community_name",
                        "value": transaction_instance.community_name
                    }
                ]
            }
        ],
        "template_name": PAYMENT_PAGE_PAYMENT_SUCCESS_MEMBER_WHATSAPP_TEMPLATE_NAME,
        "broadcast_name": PAYMENT_PAGE_PAYMENT_SUCCESS_MEMBER_WHATSAPP_BROADCAST_NAME
    }

    send_wa_messages_response = send_wa_messages(community_owner_details['id'], payment_success_whatsapp_member_body)

    return send_email_response, send_wa_messages_response


@shared_task
def payment_page_member_payment_failed_email(transaction_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                          {"payment_page_id": transaction_instance.plan_id})

    if not payment_page_filter:
        return {'error_message': "Invalid plan_id for payment page"}

    payment_page_instance = payment_page_filter[0]

    # Get Owner of community
    community_owner_details = CoreServiceUtilities.get_community_admins(transaction_instance.type_id,
                                                                        fetch_owner_only=True)

    if not community_owner_details:
        return {'error_message': "No owner found for the community"}

    community_owner_details = community_owner_details[0]

    # Community Owner email
    owner_verified_email_and_phone = get_first_verified_email_and_phone(community_owner_details['id'])

    if 'error_message' in owner_verified_email_and_phone:
        return {'error_message': owner_verified_email_and_phone['error_message']}

    member_payment_failed_mail_template = get_template(
        'payment_failed_member_email_payment_page.html').render(
        {"member_name": transaction_instance.payment_name,
         "payment_page_title": payment_page_instance.title,
         "community_name": transaction_instance.community_name,
         "community_manager_name": community_owner_details['name']})

    payment_page_mail_body_payment_failed_member = PAYMENT_PAGE_PAYMENT_FAILED_EMAIL_TO_MEMBER_BODY.copy()

    payment_page_mail_body_payment_failed_member['subject'] = payment_page_mail_body_payment_failed_member[
        'subject'].format(payment_page_instance.title)
    payment_page_mail_body_payment_failed_member['mail_body'] = member_payment_failed_mail_template
    payment_page_mail_body_payment_failed_member['mail_recipient_list'] = [transaction_instance.payment_email]
    payment_page_mail_body_payment_failed_member['reply_to'] = [owner_verified_email_and_phone['email']]

    send_email_response = send_email_from_core_service(community_owner_details['id'],
                                                       payment_page_mail_body_payment_failed_member)

    payment_success_whatsapp_member_body = {
        "receivers_list": [
            {
                "whatsappNumber": NumberUtilities.get_integer_from_string(transaction_instance.payment_phone),
                "customParams": [
                    {
                        "name": "payment_page_title",
                        "value": payment_page_instance.title
                    },
                    {
                        "name": "link",
                        "value": transaction_instance.payment_page_url
                    }
                ]
            }
        ],
        "template_name": PAYMENT_PAGE_PAYMENT_FAILED_MEMBER_WHATSAPP_TEMPLATE_NAME,
        "broadcast_name": PAYMENT_PAGE_PAYMENT_FAILED_MEMBER_WHATSAPP_BROADCAST_NAME
    }

    send_wa_messages_response = send_wa_messages(community_owner_details['id'], payment_success_whatsapp_member_body)

    return send_email_response, send_wa_messages_response


@shared_task
def payment_page_cm_payment_success_email(transaction_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    payment_page_filter = ModelUtilities.get_model_filter(PaymentPageMeta,
                                                          {"payment_page_id": transaction_instance.plan_id})

    if not payment_page_filter:
        return {'error_message': "Invalid plan_id for payment page"}

    payment_page_instance = payment_page_filter[0]

    # Get Owner of community
    community_owner_details = CoreServiceUtilities.get_community_admins(transaction_instance.type_id,
                                                                        fetch_owner_only=True)

    if not community_owner_details:
        return {'error_message': "No owner found for the community"}

    community_owner_details = community_owner_details[0]

    # Community Owner email
    owner_verified_email_and_phone = get_first_verified_email_and_phone(community_owner_details['id'])

    if 'error_message' in owner_verified_email_and_phone:
        return {'error_message': owner_verified_email_and_phone['error_message']}

    cm_payment_success_mail_template = get_template(
        'payment_success_cm_email_payment_page.html').render(
        {"member_name": transaction_instance.payment_name,
         "member_email": transaction_instance.payment_email,
         "member_phone": transaction_instance.payment_phone,
         "currency": transaction_instance.currency,
         "amount": NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount),
         "community_name": transaction_instance.community_name})

    payment_page_mail_body_payment_success_cm = PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_CM_BODY.copy()

    payment_page_mail_body_payment_success_cm['subject'] = payment_page_mail_body_payment_success_cm[
        'subject'].format(transaction_instance.community_name)
    payment_page_mail_body_payment_success_cm['mail_body'] = cm_payment_success_mail_template
    payment_page_mail_body_payment_success_cm['mail_recipient_list'] = [transaction_instance.payment_email]

    send_email_response = send_email_from_core_service(community_owner_details['id'],
                                                       payment_page_mail_body_payment_success_cm)

    return send_email_response, None


@shared_task
def cash_payment_membership_communication(transaction_id, otl_link, user_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    whatsapp_member_body = {
        "receivers_list": [
            {
                "whatsappNumber": NumberUtilities.get_integer_from_string(transaction_instance.payment_phone),
                "customParams": [
                    {
                        "name": "community_name",
                        "value": transaction_instance.community_name
                    },
                    {
                        "name": "plan_name",
                        "value": transaction_instance.plan_name
                    },
                    {
                        "name": "link",
                        "value": otl_link['private_link']
                    },
                    {
                        "name": "payment_id",
                        "value": transaction_instance.payment_id
                    }
                ]
            }
        ],
        "template_name": PAYMENT_SUCCESS_MEMBERSHIP_WHATSAPP_TEMPLATE_NAME,
        "broadcast_name": PAYMENT_SUCCESS_MEMBERSHIP_WHATSAPP_BROADCAST_NAME
    }

    send_wa_messages_response = send_wa_messages(user_id, whatsapp_member_body)

    # Get CM/Owners of community
    community_owner_details = CoreServiceUtilities.get_community_admins(transaction_instance.type_id)

    if not community_owner_details:
        return {'error_message': "No cm/owner found for the community"}

    cm_details = {}

    for member in community_owner_details:
        cm_details[member['id']] = None

    for cm in cm_details.keys():
        details = get_first_verified_email_and_phone(cm)

        if 'error_message' in details:
            continue

        cm_details[cm] = details

    cm_emails = []

    for cm in cm_details.keys():
        if cm_details[cm] is not None and cm_details[cm]['email'] is not None:
            cm_emails.append(cm_details[cm]['email'])

    cm_mail_template = get_template(
        'cash_payments/cm_email_member_join.html').render(
        {"community_name": transaction_instance.community_name,
         "member_email": transaction_instance.payment_email,
         "member_phone": transaction_instance.payment_phone,
         "otl_link": otl_link['private_link'],
         "plan_name": transaction_instance.plan_name,
         "cost": transaction_instance.amount})

    cm_mail_body = {
        "subject": PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_CM_SUBJECT,
        "mail_body": cm_mail_template,
        "mail_recipient_list": cm_emails
    }

    member_mail_template = get_template(
        'cash_payments/member_email_member_join.html').render(
        {"community_name": transaction_instance.community_name,
         "otl_link": otl_link['private_link'],
         "payment_id": transaction_instance.payment_id})

    member_mail_body = {
        "subject": PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_MEMBER_SUBJECT.format(transaction_instance.community_name),
        "mail_body": member_mail_template,
        "mail_recipient_list": [transaction_instance.payment_email],
        "reply_to": cm_emails
    }

    send_cm_email_response = send_email_from_core_service(user_id, cm_mail_body)
    send_member_email_response = send_email_from_core_service(user_id, member_mail_body)

    return send_cm_email_response, send_member_email_response, send_wa_messages_response


@shared_task
def cash_payment_renewal_communication(transaction_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    community_owner_details = CoreServiceUtilities.get_community_admins(transaction_instance.type_id)

    if not community_owner_details:
        return {'error_message': "No cm/owner found for the community"}

    cm_details = {}

    for member in community_owner_details:
        cm_details[member['id']] = None

    for cm in cm_details.keys():
        details = get_first_verified_email_and_phone(cm)

        if 'error_message' in details:
            continue

        cm_details[cm] = details

    cm_emails = []

    for cm in cm_details.keys():
        if cm_details[cm] is not None:
            cm_emails.append(cm_details[cm]['email'])

    cm_mail_template = get_template(
        'cash_payments/cm_email_member_renew.html').render(
        {"community_name": transaction_instance.community_name,
         "member_email": transaction_instance.payment_email,
         "member_phone": transaction_instance.payment_phone,
         "plan_name": transaction_instance.plan_name,
         "cost": transaction_instance.amount})

    cm_mail_body = {
        "subject": PAYMENT_SUCCESS_MEMBERSHIP_RENEW_EMAIL_TO_CM_SUBJECT.format(transaction_instance.community_name),
        "mail_body": cm_mail_template,
        "mail_recipient_list": cm_emails
    }

    send_cm_email_response = send_email_from_core_service(transaction_instance.user_id, cm_mail_body)

    return send_cm_email_response, None
