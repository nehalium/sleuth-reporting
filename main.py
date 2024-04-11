from datetime import datetime
import logging
from metricsWriter import MetricsWriter
from reportingPeriod import ReportingPeriod
from sleuthApi import SleuthApi

logging.basicConfig(level=logging.INFO)


def get_metrics_by_team(period):
    metrics = []

    sleuth_api = SleuthApi()
    teams = sleuth_api.get_teams()
    for team in teams:
        period.reset_slice()
        while period.is_still_running():
            logging.info(f"[{datetime.now()}] TEAM={team["slug"]} START={period.slice["start"]} END={period.slice["end"]}")
            metrics.append(sleuth_api.get_team_metrics(team, period.slice["start"], period.slice["end"]))
            period.update_slice()

    writer = MetricsWriter("Teams")
    writer.write_to_excel(metrics, teams)


def get_metrics_by_project(period):
    metrics = []

    sleuth_api = SleuthApi()
    projects = sleuth_api.get_projects()
    for project in projects:
        period.reset_slice()
        while period.is_still_running():
            logging.info(f"[{datetime.now()}] PROJECT={project["slug"]} START={period.slice["start"]} END={period.slice["end"]}")
            metrics.append(sleuth_api.get_project_metrics(project, period.slice["start"], period.slice["end"]))
            period.update_slice()

    writer = MetricsWriter("Projects")
    writer.write_to_excel(metrics, projects)


if __name__ == "__main__":
    period_days = 7
    reporting_period = ReportingPeriod(period_days)
    get_metrics_by_team(reporting_period)
    get_metrics_by_project(reporting_period)
