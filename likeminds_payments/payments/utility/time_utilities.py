import time


class TimeUtilities:

    @staticmethod
    def current_time_in_milliseconds() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def add_months_in_epoch_time(epoch: int, months: int) -> int:
        return epoch + months*30*86400 - 86400

    @staticmethod
    def subtract_days_in_epoch_time(epoch: int, days: int) -> int:
        return epoch - days*86400000

    @staticmethod
    def add_days_in_epoch_time(epoch: int, days: int) -> int:
        return epoch + days*86400000

    @staticmethod
    def add_milliseconds_in_epoch_time(epoch: int, milliseconds: int) -> int:
        return epoch + milliseconds
