import json

class RequestUtilities:

    @staticmethod
    def load_request_body(request):
        try:
            request_body = json.loads(request.body)
        except Exception as e:
            request_body = {}

        return request_body