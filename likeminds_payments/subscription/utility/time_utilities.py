import time

MILLISECONDS_IN_A_DAY = 86400000

days_in_months = {
    '01': 31,
    '02': 28,
    '03': 31,
    '04': 30,
    '05': 31,
    '06': 30,
    '07': 31,
    '08': 31,
    '09': 30,
    '10': 31,
    '11': 30,
    '12': 31
}


class TimeUtilities:

    @staticmethod
    def current_time_in_milliseconds() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def get_number_of_days_in_months(start_month: str, months_count: int, backward: bool = False) -> int:
        consider = False
        total_days = 0
        while months_count != 0:
            months_list = sorted(days_in_months.items())
            if backward:
                months_list = reversed(months_list)
            for k, days in months_list:
                if consider is True and months_count != 0:
                    total_days += days
                    months_count -= 1
                if k == start_month:
                    consider = True
                if months_count == 0:
                    consider = False
        return total_days

    @staticmethod
    def add_months_in_epoch_time(epoch: int, months: int) -> int:
        month = time.strftime("%m", time.gmtime(epoch))
        days = TimeUtilities.get_number_of_days_in_months(month, months)

        return epoch + days * MILLISECONDS_IN_A_DAY

    @staticmethod
    def subtract_months_in_epoch_time(epoch: int, months: int) -> int:
        month = time.strftime("%m", time.gmtime(epoch))
        days = TimeUtilities.get_number_of_days_in_months(month, months, True)

        return epoch - (days + 1) * milliseconds_in_a_day

    @staticmethod
    def subtract_days_in_epoch_time(epoch: int, days: int) -> int:
        return epoch - days * MILLISECONDS_IN_A_DAY

    @staticmethod
    def add_days_in_epoch_time(epoch: int, days: int) -> int:
        return epoch + days * MILLISECONDS_IN_A_DAY

    @staticmethod
    def add_milliseconds_in_epoch_time(epoch: int, milliseconds: int) -> int:
        return epoch + milliseconds
