
class NumberUtilities:

    @staticmethod
    def get_integer_from_string(number_string: str, return_default: int = None) -> int:
        try:
            return int(number_string)
        except (ValueError, TypeError):
            return return_default

    @staticmethod
    def convert_to_paisa_or_none(number):
        if isinstance(number, int):
            return int(number)*100
        return None
