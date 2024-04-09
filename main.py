import requests
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv
import logging
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import pandas as pd

logging.basicConfig(level=logging.INFO)

# load environmental variables
load_dotenv()
sleuth_token = os.getenv("SLEUTH_PERSONAL_TOKEN")
org_slug = os.getenv("ORG_SLUG")

# initialize globals
period_days = 7
output_dir = "output"


def get_span():
    if len(sys.argv) > 2:
        return {
            "start": datetime.strptime(sys.argv[1], '%Y-%m-%d'),
            "end": datetime.strptime(sys.argv[2], '%Y-%m-%d')
        }
    else:
        return {
            "start": datetime(datetime.now().year, 1, 1, 0, 0, 0),
            "end": datetime(datetime.now().year, 6, 30, 23, 59, 59)
        }


def generate_period(span):
    return {
        "start": span["start"],
        "end": get_next_period_start(span["start"])
    }


def increment_period(period):
    period["start"] = get_next_period_start(period["start"])
    period["end"] = get_next_period_start(period["start"])
    return period


def get_next_period_start(current_date):
    return current_date + timedelta(days=period_days)


def seconds_to_days(seconds):
    return seconds / 86400


def seconds_to_minutes(seconds):
    return seconds / 60


def zulu_from_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def write_metrics_to_excel(metric_type, metrics, items):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    file_name = f"{output_dir}/sleuth-by-{metric_type.lower()}-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx"
    df = pd.DataFrame(metrics)
    writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
    df.to_excel(writer, sheet_name=metric_type)
    for item in items:
        df_current=df.query(f"slug == '{item["slug"]}'")
        df_current.T.to_excel(writer, sheet_name=item["name"][:30])
    writer.close()


def extract_projects_list(data):
    projects_list = {
        "total_count": data["data"]["organization"]["projects"]["totalCount"],
        "projects": []
    }
    for project in data["data"]["organization"]["projects"]["edges"]:
        projects_list["projects"].append({
            "slug": project["node"]["slug"],
            "name": project["node"]["name"],
            "cursor": project["cursor"]
        })
    return projects_list


def extract_teams_list(data):
    teams_list = {
        "total_count": data["data"]["organization"]["teams"]["totalCount"],
        "teams": []
    }
    for team in data["data"]["organization"]["teams"]["edges"]:
        teams_list["teams"].append({
            "slug": team["node"]["slug"],
            "name": team["node"]["name"],
            "cursor": team["cursor"]
        })
        for subteam in team["node"]["subteams"]["edges"]:
            teams_list["teams"].append({
                "slug": subteam["node"]["slug"],
                "name": subteam["node"]["name"],
                "cursor": subteam["cursor"]
            })
            teams_list["total_count"] += 1
    return teams_list


def extract_metrics(item, start_date, end_date, data):
    return {
        "calendar_week": f"{start_date.year} - {start_date.strftime("%V")}",
        "start_date": zulu_from_datetime(start_date),
        "end_date": zulu_from_datetime(end_date),
        "slug": item["slug"],
        "name": item["name"],
        "deploys": data["data"]["organization"]["metricsRecap"]["numOfDeploys"],
        "avg_deploys": data["data"]["organization"]["metricsRecap"]["numOfDeploys"] / period_days,
        "lead_time_secs": data["data"]["organization"]["metricsRecap"]["avgLeadTimeInSec"],
        "lead_time_days": seconds_to_days(data["data"]["organization"]["metricsRecap"]["avgLeadTimeInSec"]),
        "failure_rate": data["data"]["organization"]["metricsRecap"]["failureRatePercent"],
        "mttr_secs": data["data"]["organization"]["metricsRecap"]["avgMttrDurationInSec"],
        "mttr_minutes": seconds_to_minutes(data["data"]["organization"]["metricsRecap"]["avgMttrDurationInSec"])
    }


def invoke_sleuth_api(query, variables):
    url = "https://app.sleuth.io/graphql"
    headers = {
        "Content-Type": "application/json",
        # Uncomment and replace with your actual token if authorization is required
        "Authorization": f"Bearer {sleuth_token}"
    }
    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Parsing the response JSON
        data = {
            "status": "SUCCESS",
            "payload": response.json()
        }
    else:
        data = {
            "status": "FAIL",
            "error": response.text
        }
    return data


def get_projects():
    projects_list = get_projects_page("")
    while projects_list["total_count"] > len(projects_list["projects"]):
        cursor = projects_list["projects"][-1]["cursor"]
        new_page = get_projects_page(cursor)
        projects_list["projects"].extend(new_page["projects"])
    return projects_list["projects"]


def get_projects_page(cursor):
    query = """
        query GetListOfProjects($orgSlug: ID!, $after: String!) {
            organization(orgSlug: $orgSlug) {
                projects(first: 50, after: $after) {
                    totalCount
                    edges {
                        cursor
                        node {
                            id
                            slug
                            name
                        }
                    }
                }
            }
        }
    """

    variables = f"""
        {{
            "orgSlug": "{org_slug}",
            "after": "{cursor}"
        }}
    """

    data = invoke_sleuth_api(query, variables)
    if data["status"] == "SUCCESS":
        return extract_projects_list(data["payload"])
    else:
        raise Exception(data["error"])


def get_project_metrics(project, start_date, end_date):
    query = """
        query GetNumberOfProjectDeploys($orgSlug: ID!, $start: DateTime!, $end: DateTime!, $projectSlugs: [ID]) {
            organization(orgSlug: $orgSlug) {
                metricsRecap(start: $start, end: $end, filters: {projectSlugs: $projectSlugs}) {
                    numOfDeploys
                    avgLeadTimeInSec
                    failureRatePercent
                    avgMttrDurationInSec
                }
            }
        }
    """

    variables = f"""
        {{
            "orgSlug": "{org_slug}",
            "start": "{zulu_from_datetime(start_date)}",
            "end": "{zulu_from_datetime(end_date)}",
            "projectSlugs": [
                "{project["slug"]}"
            ]
        }}
    """

    data = invoke_sleuth_api(query, variables)
    if data["status"] == "SUCCESS":
        return extract_metrics(project, start_date, end_date, data["payload"])
    else:
        raise Exception(data["error"])


def get_teams():
    teams_list = get_teams_page("")
    return teams_list["teams"]


def get_teams_page(cursor):
    query = """
        query GetListOfTeams($orgSlug: ID!, $after: String!) {
            organization(orgSlug: $orgSlug) {
                teams(first: 50, after: $after) {
                    totalCount
                    edges {
                        cursor
                        node {
                            id
                            slug
                            name
                            subteamsCount
                            subteams(first: 50) {
                                edges {
                                    cursor
                                    node {
                                        id
                                        slug
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    variables = f"""
        {{
            "orgSlug": "{org_slug}",
            "after": "{cursor}"
        }}
    """

    data = invoke_sleuth_api(query, variables)
    if data["status"] == "SUCCESS":
        return extract_teams_list(data["payload"])
    else:
        raise Exception(data["error"])


def get_team_metrics(team, start_date, end_date):
    query = """
        query GetNumberOfTeamDeploys($orgSlug: ID!, $start: DateTime!, $end: DateTime!, $teamSlugs: [ID]) {
            organization(orgSlug: $orgSlug) {
                metricsRecap(start: $start, end: $end, filters: {teamSlugs: $teamSlugs}) {
                    numOfDeploys
                    avgLeadTimeInSec
                    failureRatePercent
                    avgMttrDurationInSec
                }
            }
        }
    """

    variables = f"""
            {{
                "orgSlug": "{org_slug}",
                "start": "{zulu_from_datetime(start_date)}",
                "end": "{zulu_from_datetime(end_date)}",
                "teamSlugs": [
                    "{team["slug"]}"
                ]
            }}
    """

    data = invoke_sleuth_api(query, variables)
    if data["status"] == "SUCCESS":
        return extract_metrics(team, start_date, end_date, data["payload"])
    else:
        raise Exception(data["error"])


def get_metrics_by_team(span):
    metrics = []

    teams = get_teams()
    for team in teams:
        period = generate_period(span)
        while period["start"] < span["end"]:
            logging.info(f"TEAM={team["slug"]}, START={period["start"]}, END={period["end"]}")
            metrics.append(get_team_metrics(team, period["start"], period["end"]))
            period = increment_period(period)

    write_metrics_to_excel("Teams", metrics, teams)


def get_metrics_by_project(span):
    metrics = []

    projects = get_projects()
    for project in projects:
        period = generate_period(span)
        while period["start"] < span["end"]:
            logging.info(f"PROJECT={project["slug"]}, START={period["start"]}, END={period["end"]}")
            metrics.append(get_project_metrics(project, period["start"], period["end"]))
            period = increment_period(period)

    write_metrics_to_excel("Projects", metrics, projects)


if __name__ == "__main__":
    run_span = get_span()
    get_metrics_by_team(run_span)
    get_metrics_by_project(run_span)
