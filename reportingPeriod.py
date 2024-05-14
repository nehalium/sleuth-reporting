from datetime import datetime
import sys
from dateTimeUtils import DateTimeUtils


class ReportingPeriod:
    period_days = 7
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

    @staticmethod
    def get_span():
        if len(sys.argv) > 2:
            return {
                "start": datetime.strptime(sys.argv[1], '%Y-%m-%d'),
                "end": datetime.strptime(sys.argv[2], '%Y-%m-%d')
            }
        else:
            return {
                "start": datetime(datetime.now().year, 1, 1, 0, 0, 0),
                "end": datetime(datetime.now().year, 7, 31, 23, 59, 59)
            }

    def validate_span(self):
        span_days = DateTimeUtils.diff_days(self.time_span["start"], self.time_span["end"])
        if span_days > 270:
            raise Exception("Time span too large for batch API.")

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
