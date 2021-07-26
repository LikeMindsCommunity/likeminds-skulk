class LeadViewHelper:

    @staticmethod
    def send_facebook_event_body_validator(request_body) -> dict:

        if not request_body:
            return {'error_message': 'invalid request body'}

        body = {
            'fbc': None,
            'fbp': None,
            'emails': [],
            'phones': [],
            'event_name': None,
            'action_source': None,
            'event_source_url': None
        }

        if 'event_name' not in request_body or not request_body['event_name']:
            return {'error_message': 'send event_name'}

        if 'source' not in request_body or not request_body['source']:
            return {'error_message': 'send source'}

        if 'fbc' in request_body:
            body['fbc'] = request_body['fbc']

        if 'fbp' in request_body:
            body['fbp'] = request_body['fbp']

        if 'emails' in request_body:
            body['emails'] = request_body['emails']

        if 'phones' in request_body:
            body['phones'] = request_body['phones']

        if 'event_name' in request_body:
            body['event_name'] = request_body['event_name']

        if 'source' in request_body:
            body['action_source'] = request_body['source']

        if 'source_url' in request_body:
            body['event_source_url'] = request_body['source_url']

        return body
