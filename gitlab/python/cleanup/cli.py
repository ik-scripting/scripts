#!/usr/bin/env python3

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://gitlab.com/thelabnyc/gitlab-storage-cleanup/-/tree/master?ref_type=heads

import argparse
import os
import sys
from . import tasks

GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")


def main():
    parser = argparse.ArgumentParser(
        description="Delete old artifacts from Gitlab to reduce storage usage"
    )
    parser.add_argument(
        "project_path_pattern",
        type=str,
        help="Regex pattern controlling which projects to cleanup. E.g. '^my-group\\/'",
    )
    parser.add_argument(
        "-d",
        "--min-days-old",
        type=int,
        default=14,
        help="Don't delete anything created within the last N days. Default is 14.",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=10,
        help="Number of worker threads to use. Default is 10.",
    )
    parser.add_argument(
        "-H",
        "--hostname",
        type=str,
        default="gitlab.com",
        help="Gitlab API hostname. Default is 'gitlab.com'.",
    )

    args = parser.parse_args()

    if not GITLAB_ACCESS_TOKEN:
        sys.stderr.write(
            "Please set your Gitlab access token as the `GITLAB_ACCESS_TOKEN` environment variable."
        )
        sys.exit(1)

    # Run cleanup
    tasks.cleanup_artifacts(
        access_token=GITLAB_ACCESS_TOKEN,
        hostname=args.hostname,
        project_pattern=args.project_path_pattern,
        min_days_old=args.min_days_old,
        num_workers=args.workers,
    )
