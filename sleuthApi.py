import os
import requests
from dateTimeUtils import DateTimeUtils
from dotenv import load_dotenv

load_dotenv()


class SleuthApi:
    sleuth_token = ""
    org_slug = ""

    def __init__(self):
        self.sleuth_token = os.getenv("SLEUTH_PERSONAL_TOKEN")
        self.org_slug = os.getenv("ORG_SLUG")

    def invoke(self, query, variables):
        return self.invoke_internal({
            "query": query,
            "variables": variables
        })

    def invoke_internal(self, payload):
        url = "https://app.sleuth.io/graphql"
        headers = {
            "Content-Type": "application/json",
            # Uncomment and replace with your actual token if authorization is required
            "Authorization": f"Bearer {self.sleuth_token}"
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

    def invoke_batch(self, payload):
        url = "https://app.sleuth.io/graphql-batch"
        headers = {
            "Content-Type": "application/json",
            # Uncomment and replace with your actual token if authorization is required
            "Authorization": f"Bearer {self.sleuth_token}"
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

    def get_projects(self):
        projects_list = self.get_projects_page("")
        while projects_list["total_count"] > len(projects_list["projects"]):
            cursor = projects_list["projects"][-1]["cursor"]
            new_page = self.get_projects_page(cursor)
            projects_list["projects"].extend(new_page["projects"])
        return projects_list["projects"]

    def get_projects_page(self, cursor):
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
                "orgSlug": "{self.org_slug}",
                "after": "{cursor}"
            }}
        """

        response = self.invoke(query, variables)
        if response["status"] == "SUCCESS":
            return self.extract_projects_list(response["payload"])
        else:
            raise Exception(response["error"])

    @staticmethod
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

    def get_teams(self):
        teams_list = self.get_teams_page("")
        return teams_list["teams"]

    def get_teams_page(self, cursor):
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
                "orgSlug": "{self.org_slug}",
                "after": "{cursor}"
            }}
        """

        data = self.invoke(query, variables)
        if data["status"] == "SUCCESS":
            return self.extract_teams_list(data["payload"])
        else:
            raise Exception(data["error"])

    @staticmethod
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
            for sub_team in team["node"]["subteams"]["edges"]:
                teams_list["teams"].append({
                    "slug": sub_team["node"]["slug"],
                    "name": sub_team["node"]["name"],
                    "cursor": sub_team["cursor"]
                })
                teams_list["total_count"] += 1
        return teams_list

    def get_project_metrics_query(self, project, start_date, end_date):
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
                "orgSlug": "{self.org_slug}",
                "start": "{DateTimeUtils.zulu_from_datetime(start_date)}",
                "end": "{DateTimeUtils.zulu_from_datetime(end_date)}",
                "projectSlugs": [
                    "{project["slug"]}"
                ]
            }}
        """

        return {
            "query": query,
            "variables": variables
        }

    def get_team_metrics_query(self, team, start_date, end_date):
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
                    "orgSlug": "{self.org_slug}",
                    "start": "{DateTimeUtils.zulu_from_datetime(start_date)}",
                    "end": "{DateTimeUtils.zulu_from_datetime(end_date)}",
                    "teamSlugs": [
                        "{team["slug"]}"
                    ]
                }}
        """

        return {
            "query": query,
            "variables": variables
        }

    def get_batch_metrics(self, headers, queries):
        response = self.invoke_batch(queries)
        if response["status"] == "SUCCESS":
            return self.populate_batch_metrics(headers, response["payload"])
        else:
            raise Exception(response["error"])

    @staticmethod
    def generate_metrics_header(item, start_date, end_date):
        return {
            "calendar_week": f"{start_date.year}.{start_date.strftime("%V")}",
            "start_date": DateTimeUtils.zulu_from_datetime(start_date),
            "end_date": DateTimeUtils.zulu_from_datetime(end_date),
            "slug": item["slug"],
            "name": item["name"]
        }

    def populate_batch_metrics(self, headers, data):
        for header, data_row in zip(headers, data):
            self.populate_metrics(header, data_row)
        return headers

    def extract_metrics(self, item, start_date, end_date, data):
        header = self.generate_metrics_header(item, start_date, end_date)
        self.populate_metrics(header, data)
        return header

    @staticmethod
    def populate_metrics(header, data):
        period_days = DateTimeUtils.diff_days(header["start_date"], header["end_date"])
        metrics_row = data["data"]["organization"]["metricsRecap"]
        header["deploys"] = metrics_row["numOfDeploys"]
        header["avg_deploys"] = metrics_row["numOfDeploys"] / period_days
        header["lead_time_secs"] = metrics_row["avgLeadTimeInSec"]
        header["lead_time_days"] = DateTimeUtils.seconds_to_days(metrics_row["avgLeadTimeInSec"])
        header["failure_rate"] = metrics_row["failureRatePercent"]
        header["mttr_secs"] = metrics_row["avgMttrDurationInSec"]
        header["mttr_minutes"] = DateTimeUtils.seconds_to_minutes(metrics_row["avgMttrDurationInSec"])

    def get_project_metrics(self, project, start_date, end_date):
        query = self.get_project_metrics_query(project, start_date, end_date)
        response = self.invoke_internal(query)
        if response["status"] == "SUCCESS":
            return self.extract_metrics(project, start_date, end_date, response["payload"])
        else:
            raise Exception(response["error"])

    def get_team_metrics(self, team, start_date, end_date):
        query = self.get_team_metrics_query(team, start_date, end_date)
        response = self.invoke_internal(query)
        if response["status"] == "SUCCESS":
            return self.extract_metrics(team, start_date, end_date, response["payload"])
        else:
            raise Exception(response["error"])
