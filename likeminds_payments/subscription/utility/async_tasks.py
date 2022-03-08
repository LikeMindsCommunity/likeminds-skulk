from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from django.template.loader import get_template
from subscription.external_services.webflow.webflow_impl import WebflowImpl
from subscription.plans.constants import EVENT_PAYMENT_LINK
from subscription.plans.models import SubscriptionEventPlan
from subscription.transactions.models import Transaction
from subscription.payment_page.models import PaymentPageMeta
from subscription.settlements.models import Settlement
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
                                                 PAYMENT_PAGE_PAYMENT_SUCCESS_EMAIL_TO_CM_BODY,
                                                 PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_TITLE,
                                                 PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_SUB_TITLE,
                                                 PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_ROUTE,
                                                 NotificationCategories, NotificationSubCategories)
from subscription.settlements.constants import (SETTLEMENT_PROCESSED_EMAIL_TO_CM_SUBJECT,
                                                SETTLEMENT_FAILED_EMAIL_TO_CM_SUBJECT,
                                                SETTLEMENT_STATUS_MAP_FOR_EMAIL)
from subscription.transactions.constants import (EVENT_PAYMENT_SUCCESS_WHATSAPP_TEMPLATE_NAME,
                                                 EVENT_PAYMENT_SUCCESS_WHATSAPP_BROADCAST_NAME)
from subscription.utility.core_service_utilities import CoreServiceUtilities
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.time_utilities import TimeUtilities
from subscription.utility.number_utilities import NumberUtilities
from subscription.utility.string_utilities import StringUtilities
from subscription.utility.url_utilities import UrlUtilities
from .constants import BRANCH_LINK_BASE_URL, ADMIN_EMAIL, EmailCategories, EmailSubCategories, \
    CHATROOM_URL_WITH_COMMUNITY_ID, PAYMENT_SUCCESS_EMAIL_TO_MEMBER
from .mail_utilities import MailUtilities


def create_event_meta_for_webflow_update(event_plan_instance):
    event_plan_cost = event_plan_instance.cost

    if event_plan_instance.strike_cost:
        event_plan_cost = event_plan_instance.strike_cost

    event_meta = {
        'fields': {
            'cost': StringUtilities.get_string_from_integer(
                NumberUtilities.convert_to_rupee_or_none(event_plan_cost)),
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

    return {'success': False, 'error_message': 'Some error occurred while sending mail'}


@shared_task
def send_wa_messages_from_core_service(user_id, whatsapp_body):
    send_wa_message_response = CoreServiceUtilities.send_wa_messages(user_id, whatsapp_body)

    if send_wa_message_response.get('success'):
        return send_wa_message_response

    return {'success': False, 'error_message': 'Some error occurred while sending whatsapp messages'}


@shared_task
def send_notifications_from_core_service(user_id, notification_body):
    send_notifications_response = CoreServiceUtilities.send_notifications(user_id, notification_body)

    return {'success': True}


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
    payment_page_mail_body_payment_success_member['categories'] = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.PAYMENT_PAGE, EmailSubCategories.NEW_PAYMENT
    )

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

    send_wa_messages_response = send_wa_messages_from_core_service(community_owner_details['id'], payment_success_whatsapp_member_body)

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
         "payment_page_url": '/'.join([BRANCH_LINK_BASE_URL, transaction_instance.payment_page_url]),
         "community_name": transaction_instance.community_name,
         "community_manager_name": community_owner_details['name']})

    payment_page_mail_body_payment_failed_member = PAYMENT_PAGE_PAYMENT_FAILED_EMAIL_TO_MEMBER_BODY.copy()

    payment_page_mail_body_payment_failed_member['subject'] = payment_page_mail_body_payment_failed_member[
        'subject'].format(payment_page_instance.title)
    payment_page_mail_body_payment_failed_member['mail_body'] = member_payment_failed_mail_template
    payment_page_mail_body_payment_failed_member['mail_recipient_list'] = [transaction_instance.payment_email]
    payment_page_mail_body_payment_failed_member['reply_to'] = [owner_verified_email_and_phone['email']]
    payment_page_mail_body_payment_failed_member['categories'] = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.PAYMENT_PAGE, EmailSubCategories.FAILED_PAYMENT)

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

    send_wa_messages_response = send_wa_messages_from_core_service(community_owner_details['id'],
                                                                   payment_success_whatsapp_member_body)

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
        'subject'].format(str(payment_page_instance.title))
    payment_page_mail_body_payment_success_cm['mail_body'] = cm_payment_success_mail_template
    payment_page_mail_body_payment_success_cm['mail_recipient_list'] = [transaction_instance.payment_email]
    payment_page_mail_body_payment_success_cm['categories'] = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.PAYMENT_PAGE, EmailSubCategories.NEW_PAYMENT)

    send_email_response = send_email_from_core_service(community_owner_details['id'],
                                                       payment_page_mail_body_payment_success_cm)

    notifications_body = {
            'member_ids': [community_owner_details['id']],
            'message_payload': {
                'title': PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_TITLE,
                'sub_title': PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_SUB_TITLE.format(
                    str(transaction_instance.currency),
                    str(NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount)),
                    str(payment_page_instance.title)),
                'route': PAYMENT_PAGE_SUCCESS_PAYMENT_PUSH_NOTIFICATION_TO_CM_ROUTE
            },
            'category': {
                'category': NotificationCategories.PAYMENT_PAGE_SUCCESSFUL,
                'subcategory': NotificationSubCategories.NEW_PAYMENT_ADDED
            }
        }

    send_notifications_response = send_notifications_from_core_service(community_owner_details['id'],
                                                                       notifications_body)

    return send_email_response, send_notifications_response


@shared_task
def payment_success_membership_join_communication(transaction_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    otl_link = CoreServiceUtilities.fetch_otl_url(community_id=transaction_instance.type_id,
                                                  payment_id=transaction_instance.payment_id)

    if 'error_message' in otl_link:
        return {'error_message': otl_link['error_message']}

    # Get CM/Owners of community
    community_owner_details = CoreServiceUtilities.get_community_admins(transaction_instance.type_id)

    if not community_owner_details:
        return {'error_message': "No cm/owner found for the community"}

    cm_details = {}
    owner_id = None

    for member in community_owner_details:

        if member['is_owner']:
            owner_id = member['id']
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
                        "value": UrlUtilities.extract_part_from_url(otl_link['private_link'],
                                                                    'path', init_slash_off=True),
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

    send_wa_messages_response = send_wa_messages_from_core_service(owner_id, whatsapp_member_body)

    cm_mail_template = get_template(
        'cash_payments/cm_email_member_join.html').render(
        {"community_name": transaction_instance.community_name,
         "member_email": transaction_instance.payment_email,
         "member_phone": transaction_instance.payment_phone,
         "otl_link": otl_link['private_link'],
         "plan_name": transaction_instance.plan_name,
         "cost": NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount)})

    cm_mail_body = {
        "subject": PAYMENT_SUCCESS_MEMBERSHIP_EMAIL_TO_CM_SUBJECT,
        "mail_body": cm_mail_template,
        "mail_recipient_list": cm_emails,
        "categories": MailUtilities.get_email_category_list_using_category_subcategory(
            EmailCategories.JOIN_FLOW, EmailSubCategories.PAYMENT_SUCCESSFUL_AND_MEMBER_JOINED)
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
        "reply_to": cm_emails,
        "categories": MailUtilities.get_email_category_list_using_category_subcategory(
            EmailCategories.JOIN_FLOW, EmailSubCategories.PAYMENT_SUCCESSFUL)
    }

    send_cm_email_response = send_email_from_core_service(owner_id, cm_mail_body)
    send_member_email_response = send_email_from_core_service(owner_id, member_mail_body)

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
        if cm_details[cm] is not None and cm_details[cm]['email'] is not None:
            cm_emails.append(cm_details[cm]['email'])

    cm_mail_template = get_template(
        'cash_payments/cm_email_member_renew.html').render(
        {"community_name": transaction_instance.community_name,
         "member_email": transaction_instance.payment_email,
         "member_phone": transaction_instance.payment_phone,
         "plan_name": transaction_instance.plan_name,
         "cost": NumberUtilities.convert_to_rupee_or_none(transaction_instance.amount)})

    cm_mail_body = {
        "subject": PAYMENT_SUCCESS_MEMBERSHIP_RENEW_EMAIL_TO_CM_SUBJECT.format(transaction_instance.community_name),
        "mail_body": cm_mail_template,
        "mail_recipient_list": cm_emails
    }

    send_cm_email_response = send_email_from_core_service(transaction_instance.user_id, cm_mail_body)

    return send_cm_email_response, None


def _settlement_validator(settlement_id) -> dict:

    settlement_instance = ModelUtilities.get_model_instance_or_none(Settlement, settlement_id)

    if not settlement_instance:
        return {'error_message': "Invalid settlement_id"}

    community_details = CoreServiceUtilities.get_community_data(settlement_instance.community_id)

    if not community_details or 'community' not in community_details:
        return {'error_message': "No community details found for the community"}

    community_owner_details = CoreServiceUtilities.get_community_admins(settlement_instance.community_id)

    if not community_owner_details:
        return {'error_message': "No cm/owner found for the community"}

    return {'settlement_instance': settlement_instance,
            'community_details': community_details,
            'community_owner_details': community_owner_details}


def _get_settlement_processed_template_context(community_details, settlement_instance):

    cm_mail_template = get_template(
        'settlements/settlement_processed_cm_email.html').render(
        {"community_name": community_details['community'].get('name'),
         "currency": settlement_instance.currency,
         "amount": NumberUtilities.convert_to_rupee_or_none(settlement_instance.amount),
         "settlement_id": settlement_instance.settlement_id})

    return cm_mail_template


def _get_settlement_processed_email_context(community_details, community_owner_details, settlement_instance,
                                            template_context):

    cm_details = {}
    owner_id = None

    for member in community_owner_details:
        if member['is_owner']:
            owner_id = member['id']
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

    cm_emails.append(ADMIN_EMAIL)

    mail_categories = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.SETTLEMENT, EmailSubCategories.SETTLEMENT_SUCCESSFUL_CM)

    cm_mail_body = {
        "subject": SETTLEMENT_PROCESSED_EMAIL_TO_CM_SUBJECT.format(
            community_details['community'].get('name'),
            '{} {}'.format(TimeUtilities.convert_epoch_to_date(settlement_instance.created_at),
                           TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(settlement_instance.created_at))
        ),
        "mail_body": template_context,
        "mail_recipient_list": cm_emails,
        "categories": mail_categories
    }

    return {'email_context': cm_mail_body,
            'owner_id': owner_id}


@shared_task
def settlement_processed_communication(settlement_id):

    communication_validator = _settlement_validator(settlement_id)

    if 'error_message' in communication_validator:
        return communication_validator['error_message']

    communication_template_context = _get_settlement_processed_template_context(
        communication_validator.get('community_details'),
        communication_validator.get('settlement_instance'))

    communication_email_details = _get_settlement_processed_email_context(
        communication_validator.get('community_details'),
        communication_validator.get('community_owner_details'),
        communication_validator.get('settlement_instance'),
        communication_template_context
    )

    send_cm_email_response = send_email_from_core_service(communication_email_details.get('owner_id'),
                                                          communication_email_details.get('email_context'))

    return send_cm_email_response, None


def _get_settlement_failed_cm_template_context(community_details, settlement_instance):

    cm_mail_template = get_template(
        'settlements/settlement_failed_cm_email.html').render(
        {"community_name": community_details['community'].get('name'),
         "currency": settlement_instance.currency,
         "amount": NumberUtilities.convert_to_rupee_or_none(settlement_instance.amount),
         "settlement_id": settlement_instance.settlement_id})

    return cm_mail_template


def _get_settlement_failed_cm_email_context(community_details, community_owner_details, settlement_instance,
                                            template_context):

    cm_details = {}
    owner_id = None

    for member in community_owner_details:
        if member['is_owner']:
            owner_id = member['id']
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

    cm_emails.append(ADMIN_EMAIL)

    mail_categories = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.SETTLEMENT, EmailSubCategories.SETTLEMENT_FAILED_CM)

    cm_mail_body = {
        "subject": SETTLEMENT_FAILED_EMAIL_TO_CM_SUBJECT.format(
            community_details['community'].get('name'),
            '{} {}'.format(TimeUtilities.convert_epoch_to_date(settlement_instance.created_at),
                           TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(settlement_instance.created_at))
        ),
        "mail_body": template_context,
        "mail_recipient_list": cm_emails,
        "categories": mail_categories
    }

    return {'email_context': cm_mail_body,
            'owner_id': owner_id}


@shared_task
def settlement_failed_cm_communication(settlement_id):

    communication_validator = _settlement_validator(settlement_id)

    if 'error_message' in communication_validator:
        return communication_validator['error_message']

    communication_template_context = _get_settlement_failed_cm_template_context(
        communication_validator.get('community_details'),
        communication_validator.get('settlement_instance'))

    communication_email_details = _get_settlement_failed_cm_email_context(
        communication_validator.get('community_details'),
        communication_validator.get('community_owner_details'),
        communication_validator.get('settlement_instance'),
        communication_template_context
    )

    send_cm_email_response = send_email_from_core_service(communication_email_details.get('owner_id'),
                                                          communication_email_details.get('email_context'))

    return send_cm_email_response, None


def _get_settlement_failed_admin_template_context(community_details, settlement_instance):

    admin_mail_template = get_template(
        'settlements/settlement_failed_admin_email.html').render(
        {"community_name": community_details['community'].get('name'),
         "currency": settlement_instance.currency,
         "amount": NumberUtilities.convert_to_rupee_or_none(settlement_instance.amount),
         "settlement_id": settlement_instance.settlement_id,
         "status": SETTLEMENT_STATUS_MAP_FOR_EMAIL[settlement_instance.status]})

    return admin_mail_template


def _get_settlement_failed_admin_email_context(community_details, community_owner_details, settlement_instance,
                                               template_context):

    cm_details = {}
    owner_id = None

    for member in community_owner_details:
        if member['is_owner']:
            owner_id = member['id']
        cm_details[member['id']] = None

    mail_categories = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.SETTLEMENT, EmailSubCategories.SETTLEMENT_FAILED_ADMIN)

    admin_mail_body = {
        "subject": SETTLEMENT_FAILED_EMAIL_TO_CM_SUBJECT.format(
            community_details['community'].get('name'),
            '{} {}'.format(TimeUtilities.convert_epoch_to_date(settlement_instance.created_at),
                           TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(settlement_instance.created_at))
        ),
        "mail_body": template_context,
        "mail_recipient_list": [ADMIN_EMAIL],
        "categories": mail_categories
    }

    return {'email_context': admin_mail_body,
            'owner_id': owner_id}


@shared_task
def settlement_failed_admin_communication(settlement_id):

    communication_validator = _settlement_validator(settlement_id)

    if 'error_message' in communication_validator:
        return communication_validator['error_message']

    communication_template_context = _get_settlement_failed_admin_template_context(
        communication_validator.get('community_details'),
        communication_validator.get('settlement_instance'))

    communication_email_details = _get_settlement_failed_admin_email_context(
        communication_validator.get('community_details'),
        communication_validator.get('community_owner_details'),
        communication_validator.get('settlement_instance'),
        communication_template_context
    )

    send_cm_email_response = send_email_from_core_service(communication_email_details.get('owner_id'),
                                                          communication_email_details.get('email_context'))

    return send_cm_email_response, None


@shared_task
def send_event_payment_success_whatsapp_and_email_to_non_member(transaction_id):

    transaction_instance = ModelUtilities.get_model_instance_or_none(Transaction, transaction_id)

    if not transaction_instance:
        return {'error_message': "Invalid transaction_id"}

    event_plan_instance = SubscriptionEventPlan.get_event_plan_or_None(transaction_instance.plan_id)

    if not transaction_instance:
        return {'error_message': "Invalid event_plan_id"}

    user_id = transaction_instance.user_id

    if user_id:
        return

    # Get Owner of community
    community_owner_details = CoreServiceUtilities.get_community_admins(event_plan_instance.community_id,
                                                                        fetch_owner_only=True)

    if not community_owner_details:
        return {'error_message': "No owner found for the community"}

    user_id = community_owner_details[0]["id"]

    chatroom_data = CoreServiceUtilities.get_chatroom_data(user_id, event_plan_instance.chatroom_id)

    if "error_message" in chatroom_data:
        return chatroom_data

    chatroom_data = chatroom_data.get("chatroom")
    event_name = chatroom_data.get("header")
    event_date_time = "{} {}".format(TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(chatroom_data.get("date_time")),
                                     TimeUtilities.convert_epoch_time_to_date_month_year(chatroom_data.get("date_time")))

    link = CHATROOM_URL_WITH_COMMUNITY_ID % (str(event_plan_instance.chatroom_id),
                                             str(event_plan_instance.community_id))

    payment_success_mail_template = get_template(
        'event_comms/paid_event_reg_success_non_member.html').render(
        {"event_name": event_name,
         "event_date": TimeUtilities.convert_epoch_time_to_month_date(chatroom_data.get("date_time")),
         "event_time": TimeUtilities.convert_epoch_time_in_hh_mm_am_pm(chatroom_data.get("date_time")),
         "link": link})

    mail_body_payment_success_member = PAYMENT_SUCCESS_EMAIL_TO_MEMBER.copy()
    mail_body_payment_success_member['mail_body'] = payment_success_mail_template
    mail_body_payment_success_member['mail_recipient_list'] = [transaction_instance.payment_email]
    mail_body_payment_success_member['categories'] = MailUtilities.get_email_category_list_using_category_subcategory(
        EmailCategories.EVENT_PAYMENT, EmailSubCategories.PAYMENT_SUCCESSFUL)

    send_email_response = send_email_from_core_service(user_id, mail_body_payment_success_member)

    payment_success_whatsapp_body = {
        "receivers_list": [
            {
                "whatsappNumber": NumberUtilities.get_integer_from_string(transaction_instance.payment_phone),
                "customParams": [
                    {
                        "name": "event_name",
                        "value": event_name
                    },
                    {
                        "name": "community_name",
                        "value": transaction_instance.community_name
                    },
                    {
                        "name": "event_date_time",
                        "value": event_date_time
                    },
                    {
                        "name": "payment_id",
                        "value": transaction_instance.payment_id
                    },
                    {
                        "name": "link",
                        "value": "{}?payment_id={}".format(event_plan_instance.chatroom_id,
                                                           transaction_instance.payment_id)
                    }
                ]
            }
        ],
        "template_name": EVENT_PAYMENT_SUCCESS_WHATSAPP_TEMPLATE_NAME,
        "broadcast_name": EVENT_PAYMENT_SUCCESS_WHATSAPP_BROADCAST_NAME
    }

    send_wa_messages_response = send_wa_messages_from_core_service(user_id, payment_success_whatsapp_body)
    return send_email_response, send_wa_messages_response
