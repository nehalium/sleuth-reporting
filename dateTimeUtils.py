from datetime import timedelta, datetime


class DateTimeUtils:
    zulu_time_format = "%Y-%m-%dT%H:%M:%SZ"

    @staticmethod
    def add_days(num_of_days, current_date):
        return current_date + timedelta(days=num_of_days)

    @staticmethod
    def add_weeks(num_of_weeks, current_date):
        return current_date + timedelta(weeks=num_of_weeks)

    @staticmethod
    def diff_days(start_date, end_date):
        delta = end_date - start_date
        return delta.days

    @staticmethod
    def shift_to_weekday(week_day, current_date, shift_forward=False):
        days_to_shift = (current_date.weekday() - week_day + 7) % 7
        if shift_forward:
            return DateTimeUtils.add_days(days_to_shift, current_date)
        else:
            return DateTimeUtils.add_days(-days_to_shift, current_date)

    @staticmethod
    def diff_days_str(start_date_as_str, end_date_as_str):
        return DateTimeUtils.diff_days(DateTimeUtils.str_to_date(start_date_as_str), DateTimeUtils.str_to_date(end_date_as_str))

    @staticmethod
    def str_to_date(date_as_str):
        return datetime.strptime(date_as_str, DateTimeUtils.zulu_time_format)

    @staticmethod
    def seconds_to_days(seconds):
        return seconds / 86400

    @staticmethod
    def seconds_to_minutes(seconds):
        return seconds / 60

    @staticmethod
    def zulu_from_datetime(dt):
        return dt.strftime(DateTimeUtils.zulu_time_format)
