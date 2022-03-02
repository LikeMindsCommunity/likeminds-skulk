from .constants import VALID_PAYOUT_WEBHOOK_EVENTS, SETTLEMENT_ERROR_SUBJECT, SETTLEMENT_ERROR_RECEIVER_LIST
from ..utility.response_utilities import ResponseUtilities
from ..utility.mail_utilities import MailUtilities
from ..utility.constants import EmailCategories, EmailSubCategories
from ..external_services.email.email_wrapper import MailWrapper

class SettlementViewHelper:

    @staticmethod
    def initiate_settlement_body_validator(request_body, member_id):

        if not request_body:
            return ResponseUtilities.get_inner_error_context('invalid request body')

        if 'community_id' not in request_body:
            return ResponseUtilities.get_inner_error_context('send community_id in body')

        if not member_id:
            return ResponseUtilities.get_inner_error_context('send member_id in headers')

        return request_body

    @staticmethod
    def create_settlement_body_validator(request_body):

        if not request_body:
            return ResponseUtilities.get_inner_error_context('invalid request body')

        if 'event' not in request_body or request_body['event'] not in VALID_PAYOUT_WEBHOOK_EVENTS:
            return ResponseUtilities.get_inner_error_context('invalid event recognized')

        if 'payload' not in request_body or not request_body['payload']:
            return ResponseUtilities.get_inner_error_context('no payload detected')

        if 'payout' not in request_body['payload'] or not request_body['payload']['payout']:
            return ResponseUtilities.get_inner_error_context('no payout object detected')

        if 'entity' not in request_body['payload']['payout'] or not request_body['payload']['payout']['entity']:
            return ResponseUtilities.get_inner_error_context('no entity object detected')

        return request_body

    @staticmethod
    def get_settlements_query_params(request):

        query_params = {
            'community_id': request.GET.get('community_id', None),
            'created_at__gte': request.GET.get('start_epoch', None),
            'created_at__lte': request.GET.get('end_epoch', None),
            'status': request.GET.get('status', None)
        }

        if not query_params['community_id']:
            return ResponseUtilities.get_inner_error_context('send community_id in query params')

        output = {}

        for param in query_params.keys():
            if query_params[param] is not None:
                output[param] = query_params[param]

        return output

    @staticmethod
    def send_webhook_failed_communication(response):

        categories = MailUtilities.get_email_category_list_using_category_subcategory(
            EmailCategories.LOGGING, EmailSubCategories.SETTLEMENT_WEBHOOK_ERROR)

        MailWrapper.send_email(SETTLEMENT_ERROR_SUBJECT, str(response),
                               SETTLEMENT_ERROR_RECEIVER_LIST, categories=categories)
