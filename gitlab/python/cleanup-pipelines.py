#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Written by Ivan Katliarchuk
# GitHub: https://github.com/ivankatliarchuk
# Website: https://ivankatliarchuk.github.io/
#
# Note: This code is a stop-gap to erase Job Pipelines for a project. I HIGHLY recommend you leverage
#
#  pip install requests
# python3 gitlab/python/cleanup-pipelines.py  --pipelines
# python3 gitlab/python/cleanup-pipelines.py  --jobs

import os, time, argparse, json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import date, datetime, timezone, timedelta

GITLAB_URL = "https://gitlab.com"
BASE_URL = f"{GITLAB_URL}/api/v4"
PROJECT_ID = os.getenv("PROJECT_ID")  # PROJECT_ID in repo settings -> general
PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")
PER_PAGE = 100
TOTAL_PAGES = 50
DAYS_OFFSET = 30 * 7

# https://docs.gitlab.com/ee/api/rest/index.html#pagination

headers = {
        "Private-Token": PRIVATE_TOKEN
    }

def json_prettify(data):
    return json.dumps(data, indent=4, default=str)

def hours_since(date_str, target_timezone=timezone.utc):
    # Parse the date string with UTC timezone
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Convert the date object to the target timezone
    date_obj_aware = date_obj.replace(tzinfo=target_timezone)

    # Get current time in the target timezone
    now_aware = datetime.now(target_timezone)

    # Calculate time difference in seconds
    delta = now_aware - date_obj_aware

    # Convert time difference to hours (float)
    hours = delta.total_seconds() / 3600
    return hours

jobs_to_erase = []
pipelines = []

def fetch_gitlab_jobs(gitlab_url, private_token, project_id):
    x_page = 1
    x_next_page = 0
    # Base URL for GitLab API endpoints
    base_url = f"{gitlab_url}/api/v4"

    while True:
        # https://docs.gitlab.com/ee/api/jobs.html
        # Construct URL for fetching jobs
        url = f"{base_url}/projects/{project_id}/jobs?scope[]=failed&scope[]=canceled&scope[]=success&per_page={PER_PAGE}&page={x_page}&sort=desc"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch jobs: {response.status_code} {response.text}")
            return

        res_headers = response.headers
        jobs = response.json()
        if not jobs:
            print("No more jobs found.")
            break

        for el in jobs:
            # print(json_prettify(el))
            # break
            job = Job(el)
            # if "tf:plan:" in job.name and job.hours_since_finished > 2:
            jobs_to_erase.append(job)

        return_next_page = int(res_headers['x-next-page'])
        if return_next_page > x_next_page and return_next_page <= TOTAL_PAGES:
            x_next_page = return_next_page
            x_page = return_next_page
            if len(jobs_to_erase) > 0:
                print(f"found jobs to erase:{len(jobs_to_erase)}")
        else:
            return
        time.sleep(0.01)

def erase_jobs(gitlab_url, private_token, project_id, jobs):
    print(f"ready to erase '{len(jobs)}' jobs.")
    base_url = f"{gitlab_url}/api/v4"
    count = 0
    for job in jobs:
        # https://docs.gitlab.com/ee/api/jobs.html#erase-a-job
        url = f"{base_url}/projects/{project_id}/jobs/{job.id}/erase"
        response = requests.post(url, headers=headers)

        if response.status_code in [201, 202]:
            pass
        else:
            print(f"Error erasing job: {response.status_code} - {response.text} and job {job.erased_at}")
            return False

        count += 1
        time.sleep(0.01)
        if count % 100 == 0:
            left = len(jobs) - count
            print(f"deleted '{count}' out of '{len(jobs)}' and left '{left}'.")

class Job:
    # https://docs.gitlab.com/ee/api/jobs.html
    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.id = data['id']
        self.finished_at = data['finished_at']
        self.hours_since_finished = hours_since(self.finished_at)
        self.erased_at = data['erased_at']

def fetch_gitlab_pipelines(gitlab_url, private_token, project_id):
    x_page = 1
    x_next_page = 0
    # Base URL for GitLab API endpoints
    base_url = f"{gitlab_url}/api/v4"
    today = date.today()
    offset_date = today - timedelta(days=DAYS_OFFSET)
    updated_before = offset_date.isoformat()
    print(f"should be updated before date {updated_before}")

    while True:
        # https://docs.gitlab.com/ee/api/pipelines.html
        # Construct URL for fetching pipelines
        # pagination=f"sort=asc"
        url = f"{base_url}/projects/{project_id}/pipelines?scope=finished&per_page={PER_PAGE}&page={x_page}&updated_before={updated_before}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch jobs: {response.status_code} {response.text}")
            return

        res_headers = response.headers
        res = response.json()
        if not res:
            print("No more jobs found.")
            break

        for el in res:
            # print(json_prettify(el))
            # break
            pipelines.append(Pipeline(el))

        return_next_page = int(res_headers['x-next-page'])
        if return_next_page > x_next_page and return_next_page <= TOTAL_PAGES:
            x_next_page = return_next_page
            x_page = return_next_page
            if len(pipelines) > 0:
                print(f"found pipelines to erase:{len(pipelines)}")
        else:
            return
        time.sleep(0.01)

def erase_pipelines(gitlab_url, private_token, project_id, pipelines):
    # https://docs.gitlab.com/ee/api/pipelines.html#delete-a-pipeline
    print(f"ready to erase '{len(pipelines)}' pipelines.")
    count = 0
    for el in pipelines:
        url = f"{BASE_URL}/projects/{project_id}/pipelines/{el.id}"
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            pass
        else:
            print(f"Error deleting pipeline: {el.id} - {response.status_code} - {response.text}")

        count += 1
        if count % 100 == 0:
            left = len(pipelines) - count
            print(f"deleted '{count}' out of '{len(pipelines)}' and left '{left}'.")

        time.sleep(0.001)

class Pipeline:
    # https://docs.gitlab.com/ee/api/pipelines.html
    def __init__(self, data):
        self.data = data
        self.id = data['id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI to cleanup Gitlab Jobs or Artifacts")
    parser.add_argument('--pipelines', action='store_true', help = "Cleanup pipelines")
    parser.add_argument('--jobs', action='store_true', help = "Cleanup jobs")
    args = parser.parse_args()

    start_time = time.time()
    if args.pipelines:
        fetch_gitlab_pipelines(GITLAB_URL, PROJECT_ID, PROJECT_ID)
        erase_pipelines(GITLAB_URL, PROJECT_ID, PROJECT_ID, pipelines)
        entities = len(pipelines)
    if args.jobs:
        fetch_gitlab_jobs(GITLAB_URL, PROJECT_ID, PROJECT_ID)
        erase_jobs(GITLAB_URL, PROJECT_ID, PROJECT_ID, jobs_to_erase)
        entities = len(jobs_to_erase)

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    duration = f"Total duration is '{int(minutes)}m:{int(seconds)}s' to process '{entities}' entities."
    print(duration)
