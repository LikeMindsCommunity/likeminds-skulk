import time


class TimeUtilities:

    @staticmethod
    def current_time_in_milliseconds() -> int:
        return int((time.time() * 1000))

    @staticmethod
    def add_months_in_epoch_time(epoch: int, months: int) -> int:
        return epoch + months*30*86400 - 86400
