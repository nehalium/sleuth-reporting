from datetime import datetime
import logging
from metricsWriter import MetricsWriter
from reportingPeriod import ReportingPeriod
from sleuthApi import SleuthApi

logging.basicConfig(level=logging.INFO)


def get_metrics_by_team(period):
    queries = []
    headers = []

    sleuth_api = SleuthApi()
    teams = sleuth_api.get_teams()
    for team in teams:
        period.reset_slice()
        while period.is_still_running():
            headers.append(sleuth_api.generate_metrics_header(team, period.slice["start"], period.slice["end"]))
            queries.append(sleuth_api.get_team_metrics_query(team, period.slice["start"], period.slice["end"]))
            period.update_slice()

    logging.info(f"[{datetime.now()}] Running teams query...")
    metrics = sleuth_api.get_batch_metrics(headers, queries)

    logging.info(f"[{datetime.now()}] Writing results...")
    writer = MetricsWriter("Teams")
    writer.write_to_excel(metrics, teams)

    logging.info(f"[{datetime.now()}] Done.")


def get_metrics_by_project(period):
    queries = []
    headers = []

    sleuth_api = SleuthApi()
    projects = sleuth_api.get_projects()
    for project in projects:
        period.reset_slice()
        while period.is_still_running():
            headers.append(sleuth_api.generate_metrics_header(project, period.slice["start"], period.slice["end"]))
            queries.append(sleuth_api.get_project_metrics_query(project, period.slice["start"], period.slice["end"]))
            period.update_slice()

    logging.info(f"[{datetime.now()}] Running projects query...")
    metrics = sleuth_api.get_batch_metrics(headers, queries)

    logging.info(f"[{datetime.now()}] Writing results...")
    writer = MetricsWriter("Projects")
    writer.write_to_excel(metrics, projects)

    logging.info(f"[{datetime.now()}] Done.")


if __name__ == "__main__":
    period_days = 7
    reporting_period = ReportingPeriod(period_days)
    get_metrics_by_team(reporting_period)
    get_metrics_by_project(reporting_period)
