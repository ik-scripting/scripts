from collections import namedtuple
from datetime import datetime, timedelta
from tqdm import tqdm
import pytz
import threading
import queue
from . import api


CleanupTask = namedtuple("CleanupTask", ["pbar", "project", "job"])


def _process_job_artifact_queue(
    access_token,
    hostname,
    pending_tasks,
    stop_event,
):
    while True:
        try:
            task = pending_tasks.get_nowait()
            api.delete_job_artifacts(access_token, hostname, task.project, task.job)
            task.pbar.update(1)
            pending_tasks.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            tqdm.write(e)
        # If the queue is empty wait to see if we the thread should exit.
        if pending_tasks.empty() and stop_event.wait(1):
            return


def cleanup_artifacts(
    access_token,
    hostname,
    project_pattern,
    min_days_old,
    num_workers,
):
    pending_tasks = queue.Queue(maxsize=num_workers * 2)
    stop_event = threading.Event()

    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    max_created_at_dt = now - timedelta(days=min_days_old)

    # Start worker threads
    thread_args = [
        access_token,
        hostname,
        pending_tasks,
        stop_event,
    ]
    workers = [
        threading.Thread(target=_process_job_artifact_queue, args=thread_args)
        for i in range(num_workers)
    ]
    for worker in workers:
        worker.start()

    # Iterate over all the projects that match the path filter.
    for project_pbar, project in api.list_projects(
        access_token, hostname, project_pattern
    ):
        # Delete artifacts tied to the project
        api.delete_project_artifacts(access_token, hostname, project)
        # Iterate over all the jobs in the project that match the date filter.
        for job_pbar, job in api.list_jobs(
            access_token, hostname, project, max_created_at_dt
        ):
            # Queue a task to delete artifacts tied to the job
            pending_tasks.put(
                CleanupTask(
                    pbar=job_pbar,
                    project=project,
                    job=job,
                )
            )
        # Wait for all the queued tasks to finish, then proceed to the next project
        pending_tasks.join()
        project_pbar.update(1)

    # Wait for all the queued tasks to finish and all the worker threads to exit
    stop_event.set()
    pending_tasks.join()
    for worker in workers:
        worker.join()
