class BooleanUtilities:

    @staticmethod
    def get_boolean_for_string(boolean_str: str):
        if boolean_str.lower() == "true":
            return True

        return False
