import json


class JsonUtilities:

    @staticmethod
    def load_json(data):

        try:
            loaded_data = json.loads(data)

        except Exception as e:

            loaded_data = {}

        return loaded_data

    @staticmethod
    def dump_json(data):

        try:
            dump_data = json.dumps(data)

        except Exception as e:
            dump_data = None

        return dump_data

