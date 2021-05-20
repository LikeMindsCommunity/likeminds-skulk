import time


class TimeUtilities:

    @staticmethod
    def current_time_in_milliseconds() -> int:
        return int((time.time() * 1000))