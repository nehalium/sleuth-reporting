from datetime import timedelta, datetime


class DateTimeUtils:
    zulu_time_format = "%Y-%m-%dT%H:%M:%SZ"

    @staticmethod
    def add_days(num_of_days, current_date):
        return current_date + timedelta(days=num_of_days)

    @staticmethod
    def diff_days(start_date, end_date):
        delta = DateTimeUtils.str_to_date(end_date) - DateTimeUtils.str_to_date(start_date)
        return delta.days

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
