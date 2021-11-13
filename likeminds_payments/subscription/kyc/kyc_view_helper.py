from ..utility.number_utilities import NumberUtilities


class KycViewHelper:

    @staticmethod
    def create_kyc_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id in body'}

        if 'name' not in request_body or not request_body['name']:
            return {'error_message': 'send name in body'}

        if 'address' not in request_body or not request_body['address']:
            return {'error_message': 'send address in body'}

        if 'doc_type' not in request_body:
            return {'error_message': 'send doc_type in body'}

        if 'doc_number' not in request_body or not request_body['doc_number']:
            return {'error_message': 'send doc_number in body'}

        if 'doc_pan_number' not in request_body or not request_body['doc_pan_number']:
            return {'error_message': 'send doc_pan_number in body'}

        if 'gstn' not in request_body or not request_body['gstn']:
            return {'error_message': 'send gstn in body'}

        if 'bank_user_name' not in request_body or not request_body['bank_user_name']:
            return {'error_message': 'send bank_user_name in body'}

        if 'bank_ifsc_code' not in request_body or not request_body['bank_ifsc_code']:
            return {'error_message': 'send bank_ifsc_code in body'}

        if 'account_number' not in request_body or not request_body['account_number']:
            return {'error_message': 'send account_number in body'}

        if 'bank_name' not in request_body or not request_body['bank_name']:
            return {'error_message': 'send bank_name in body'}

        return request_body

    @staticmethod
    def upload_kyc_body_validator(request_body, user_id):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if not user_id:
            return {'error_message': 'send x-member-id in headers'}

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id in body'}

        body = {
            'doc_front_url': request_body.get('doc_front_url', None),
            'doc_back_url': request_body.get('doc_back_url', None),
            'doc_pan_url': request_body.get('doc_pan_url', None),
            'community_id': request_body.get('community_id')
        }

        fields_list = [body['doc_front_url'], body['doc_back_url'], body['doc_pan_url']]

        if fields_list.count(None) == len(fields_list):
            return {'error_message': 'send doc_front_url/doc_back_url/doc_pan_url in body'}

        return body

    @staticmethod
    def fetch_kyc_validator(request_params, user_id, x_username, x_password):

        if not request_params:
            return {'error_message': 'invalid request params'}

        if 'community_id' not in request_params or not request_params['community_id']:
            return {'error_message': 'send community_id in params'}

        body = {'community_id': request_params.get('community_id'),
                'x_username': x_username if x_username != '' else None,
                'x_password': x_password if x_password != '' else None,
                'member_id': user_id if user_id != '' else None}

        return body

    @staticmethod
    def fetch_all_kyc_validator(request_params, x_username, x_password):

        body = {
            'page': 1,
            'x_username': x_username if x_username != '' else None,
            'x_password': x_password if x_password != '' else None}

        if 'page' in request_params:
            body['page'] = NumberUtilities.get_integer_from_string(request_params.get('page'))

        return body

    @staticmethod
    def edit_kyc_body_validator(request_body, x_username, x_password):

        if not request_body:
            return {'error_message': 'invalid request body'}

        if x_username == '':
            return {'error_message': 'send x-username in headers'}

        if x_password == '':
            return {'error_message': 'send x-password in headers'}

        if 'community_id' not in request_body or not request_body['community_id']:
            return {'error_message': 'send community_id in body'}

        return request_body
