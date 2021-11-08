from django.conf import settings
import json
import requests
from requests.auth import HTTPBasicAuth
from .constants import *
from ..razorpay.razorpayX_manager import RazorpayXManager


class RazorpayXWrapper(RazorpayXManager):

    key_id = None
    key_secret = None

    def __init__(self) -> None:

        self.key_id = settings.RAZORPAY_X_KEY
        self.key_secret = settings.RAZORPAY_X_SECRET

    def get_key_id(self) -> str:
        return self.key_id

    def get_key_secret(self) -> str:
        return self.key_secret

    @staticmethod
    def _create_contact_api_payload(contact_info) -> dict:

        if not contact_info:
            return {'error_message': 'send contact info'}

        if 'name' not in contact_info:
            return {'error_message': 'send contact name'}

        if 'user_id' not in contact_info:
            return {'error_message': 'send user_id'}

        payload = {
            'headers': {
                'Content-Type': 'application/json'
            },
            'data': {
                'name': contact_info.get('name'),
                'reference_id': '{}'.format(contact_info.get('user_id'))
            }
        }

        return payload

    def create_contact(self, contact_info) -> dict:

        api_payload = self._create_contact_api_payload(contact_info)
        api_response = requests.post(url=CONTACTS_API,
                                     headers=api_payload.get('headers'),
                                     data=json.dumps(api_payload.get('data')),
                                     auth=HTTPBasicAuth(self.get_key_id(), self.get_key_secret()))

        if hasattr(api_response, 'status_code') and int(api_response.status_code) not in [200, 201]:
            return {'error_message': 'message: {}'.format(api_response.content.decode('utf-8'))}

        return {'contact': json.loads(api_response.content)}

    @staticmethod
    def _create_account_api_payload(account_info) -> dict:

        if not account_info:
            return {'error_message': 'send account info'}

        if 'contact_id' not in account_info:
            return {'error_message': 'send contact id'}

        if 'account_type' not in account_info:
            return {'error_message': 'send account_type'}

        if 'bank_account' not in account_info:
            return {'error_message': 'send bank_account'}

        payload = {
            'headers': {
                'Content-Type': 'application/json'
            },
            'data': account_info
        }

        return payload

    def create_fund_account(self, account_info) -> dict:

        api_payload = self._create_account_api_payload(account_info)
        api_response = requests.post(url=FUND_ACCOUNTS_API,
                                     headers=api_payload.get('headers'),
                                     data=json.dumps(api_payload.get('data')),
                                     auth=HTTPBasicAuth(self.get_key_id(), self.get_key_secret()))

        if hasattr(api_response, 'status_code') and int(api_response.status_code) not in [200, 201]:
            return {'error_message': 'message: {}'.format(api_response.content.decode('utf-8'))}

        return {'account': json.loads(api_response.content)}
