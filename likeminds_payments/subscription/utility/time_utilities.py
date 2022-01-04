import math
import time
import datetime


class TimeUtilities:
    MILLISECONDS_IN_A_DAY = 86400000

    DAYS_IN_A_WEEK = 7

    DAYS_IN_MONTHS = {
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

    @staticmethod
    def current_time_in_milliseconds() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def get_number_of_days_in_months(start_month: str, months_count: int, backward: bool = False) -> int:
        consider = False
        total_days = 0
        while months_count != 0:
            months_list = sorted(TimeUtilities.DAYS_IN_MONTHS.items())
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

        return epoch + days * TimeUtilities.MILLISECONDS_IN_A_DAY

    @staticmethod
    def subtract_months_in_epoch_time(epoch: int, months: int) -> int:
        month = time.strftime("%m", time.gmtime(epoch))
        days = TimeUtilities.get_number_of_days_in_months(month, months, True)

        return epoch - days * TimeUtilities.MILLISECONDS_IN_A_DAY

    @staticmethod
    def add_weeks_in_epoch_time(epoch: int, weeks: int) -> int:
        days = weeks * TimeUtilities.DAYS_IN_A_WEEK
        return TimeUtilities.add_days_in_epoch_time(epoch, days)

    @staticmethod
    def subtract_days_in_epoch_time(epoch: int, days: int) -> int:
        return epoch - days * TimeUtilities.MILLISECONDS_IN_A_DAY

    @staticmethod
    def add_days_in_epoch_time(epoch: int, days: int) -> int:
        return epoch + days * TimeUtilities.MILLISECONDS_IN_A_DAY

    @staticmethod
    def add_milliseconds_in_epoch_time(epoch: int, milliseconds: int) -> int:
        return epoch + milliseconds

    @staticmethod
    def convert_epoch_to_date(epoch: int) -> str:
        return time.strftime('%d %b %Y', time.gmtime(epoch // 1000))

    @staticmethod
    def convert_milliseconds_to_sec(millisec) -> int:
        return millisec // 1000

    @staticmethod
    def is_epoch_in_milliseconds(epoch_time) -> bool:

        if math.floor(math.log10(epoch_time) + 1) == 13:
            return True

        return False

    @staticmethod
    def convert_epoch_time_to_date_month_year(epoch_time) -> str:

        """format -- 09 March 2021"""

        if TimeUtilities.is_epoch_in_milliseconds(epoch_time):
            epoch_time = TimeUtilities.convert_milliseconds_to_sec(epoch_time)

        return time.strftime('%d %B %Y', time.localtime(epoch_time))

    @staticmethod
    def convert_epoch_time_in_hh_mm_am_pm(epoch_time):

        """format -- hh:mm am/pm"""

        if TimeUtilities.is_epoch_in_milliseconds(epoch_time):
            epoch_time = TimeUtilities.convert_milliseconds_to_sec(epoch_time)

        return time.strftime('%I:%M %p', time.localtime(epoch_time))

    @staticmethod
    def convert_epoch_to_month_year_format(epoch: int) -> str:

        if TimeUtilities.is_epoch_in_milliseconds(epoch):
            epoch = TimeUtilities.convert_milliseconds_to_sec(epoch)

        return time.strftime('%b %Y', time.gmtime(epoch))


    @staticmethod
    def get_current_date():

        now = datetime.datetime.now()

        date = {
            'day': now.day,
            'month': now.month,
            'year': now.year
        }

        return date

    @staticmethod
    def convert_date_to_epoch(day: int, month: int, year: int):
        """converts date to epoch in milliseconds"""

        return datetime.datetime(year, month, day).timestamp()*1000

