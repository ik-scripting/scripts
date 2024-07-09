from tqdm import tqdm
import time
import requests
import dateutil.parser
import re
import threading

thread_local = threading.local()
thread_local.rsession = None


def get_rsession(access_token):
    if not getattr(thread_local, "rsession", None):
        rsession = requests.Session()
        rsession.headers.update(
            {
                "private-token": access_token,
            }
        )
        thread_local.rsession = rsession
    return thread_local.rsession


def _load_all_objects(access_token, url, desc=None):
    """
    Given the URL of a paged Gitlab API endpoint, yield all of the objects in
    all of the pages.
    """
    # First, make a HEAD request to get the stats (needed for the progress bar)
    rsession = get_rsession(access_token)
    response = rsession.head(url)
    total = int(response.headers["x-total"]) if "x-total" in response.headers else None
    failures = 0
    with tqdm(total=total, desc=desc) as pbar:
        # As long as  we have a URL for a next page, continue looping
        while url:
            if failures >= 5:
                return

            response = rsession.get(url)

            # On error, sleep a bit and try again
            if response.status_code in [500, 429]:
                tqdm.write(f"Status {response.status_code}, retrying.")
                failures += 1
                time.sleep(30)
                continue

            # Yield all the objects
            response.raise_for_status()
            page = response.json()
            for obj in page:
                yield pbar, obj

            # Continue to next page
            url = response.links.get("next", {}).get("url", None)


def delete_job_artifacts(access_token, hostname, project, job):
    rsession = get_rsession(access_token)
    project_id = project["id"]
    project_name = project["name_with_namespace"]
    job_id = job["id"]
    job_created_at = job["created_at"]
    resp = rsession.delete(
        f"https://{hostname}/api/v4/projects/{project_id}/jobs/{job_id}/artifacts"
    )
    tqdm.write(
        f"Removed job artifacts [{project_name}, Job #{job_id}, Created {job_created_at}] - status: {resp.status_code}"
    )


def delete_project_artifacts(access_token, hostname, project):
    rsession = get_rsession(access_token)
    project_id = project["id"]
    project_name = project["name_with_namespace"]
    resp = rsession.delete(f"https://{hostname}/api/v4/projects/{project_id}/artifacts")
    tqdm.write(
        f"Removed project artifacts [{project_name}] - status: {resp.status_code}"
    )


def list_projects(access_token, hostname, path_filter):
    projects = _load_all_objects(
        access_token,
        f"https://{hostname}/api/v4/projects?owned=true&per_page=100&order_by=id&page=1",
        desc="Projects",
    )
    for pbar, project in projects:
        if re.match(path_filter, project["path_with_namespace"]):
            yield pbar, project
        else:
            pbar.update(1)


def list_jobs(access_token, hostname, project, max_created_at_dt):
    project_id = project["id"]
    project_name = project["name_with_namespace"]
    jobs = _load_all_objects(
        access_token,
        f"https://{hostname}/api/v4/projects/{project_id}/jobs?per_page=100&page=1",
        desc=f"Jobs [{project_name}]",
    )
    for pbar, job in jobs:
        created_at = dateutil.parser.parse(job["created_at"])
        is_old = created_at < max_created_at_dt
        has_artifacts = job.get("artifacts_file", None) or job.get("artifacts", None)
        if is_old and has_artifacts:
            yield pbar, job
        else:
            pbar.update(1)
