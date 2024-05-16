from datetime import datetime
import sys
from dateTimeUtils import DateTimeUtils


class ReportingPeriod:
    period_days = 7  # 1 week
    start_weekday = 0  # Monday
    start_offset_weeks = 12  # 3 months
    end_offset_weeks = 1  # 1 week
    time_span = {}
    time_slice = {}

    def __init__(self, period_days):
        self.period_days = period_days
        self.time_span = self.get_span()
        self.validate_span()

    @property
    def span(self):
        return self.time_span

    @property
    def slice(self):
        return self.time_slice

    def get_span(self):
        if len(sys.argv) > 2:
            return {
                "start": datetime.strptime(sys.argv[1], '%Y-%m-%d'),
                "end": datetime.strptime(sys.argv[2], '%Y-%m-%d')
            }
        else:
            today = datetime.now()
            start_date = DateTimeUtils.add_weeks(-self.start_offset_weeks, today)
            start_date = DateTimeUtils.shift_to_weekday(self.start_weekday, start_date)
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = DateTimeUtils.add_weeks(self.end_offset_weeks, today)
            end_date = DateTimeUtils.shift_to_weekday((6 + self.start_weekday) % 7, end_date)
            end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            return {
                "start": start_date,
                "end": end_date
            }

    def validate_span(self):
        span_days = DateTimeUtils.diff_days(self.time_span["start"], self.time_span["end"])
        if span_days > 200:
            raise Warning("Time span is very large for the API.")

    def reset_slice(self):
        self.time_slice = {
            "start": self.span["start"],
            "end": self.get_next_period_start(self.span["start"])
        }

    def update_slice(self):
        self.time_slice["start"] = self.get_next_period_start(self.time_slice["start"])
        self.time_slice["end"] = self.get_next_period_start(self.time_slice["start"])

    def get_next_period_start(self, current_date):
        return DateTimeUtils.add_days(self.period_days, current_date)

    def is_still_running(self):
        return self.time_slice["start"] < self.time_span["end"]
