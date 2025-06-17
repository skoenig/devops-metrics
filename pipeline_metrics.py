#!/usr/bin/env python3

import os
import sys
import datetime

from functools import partial
from fnmatch import fnmatch

from git_metrics.process import mk_run
from git_metrics.git_metrics_release_lead_time import fetch_tags_and_author_dates

from google.cloud.devtools.cloudbuild import CloudBuildClient
from google.auth.exceptions import DefaultCredentialsError


def pipeline_time(project_id=None, build_id=None):
    if project_id is None:
        if os.environ.get("PROJECT_ID"):
            project_id = os.environ.get("PROJECT_ID")
        else:
            print("metric pipeline_time requires PROJECT_ID", file=sys.stderr)
            return

    if build_id is None:
        if os.environ.get("BUILD_ID"):
            build_id = os.environ.get("BUILD_ID")
        else:
            print("metric pipeline_time requires BUILD_ID", file=sys.stderr)
            return

    try:
        cb = CloudBuildClient()
        build = cb.get_build(project_id=project_id, id=build_id)
        pipeline_time = (
            datetime.datetime.now(tz=datetime.timezone.utc) - build.start_time
        )
        print(f"pipeline_time: {pipeline_time.total_seconds()}")
    except DefaultCredentialsError:
        print(
            "metric pipeline_time requires Application Default Credentials",
            file=sys.stderr,
        )
        return


def lead_time(deploy_tag_pattern="*", start_date=None, repo_path=None, tag_name=None):
    # Traverse only through the revision history from a certain cutoff time,
    # otherwise examining large repositories will take significant time.
    if start_date is None:
        cutoff = datetime.datetime.now() + datetime.timedelta(weeks=-12)
        start_date = int(cutoff.timestamp())

    if repo_path is None:
        if os.environ.get("REPO_PATH"):
            repo_path = os.environ.get("REPO_PATH")
        else:
            print("metric lead_time requires REPO_PATH", file=sys.stderr)
            return

    if tag_name is None:
        if os.environ.get("TAG_NAME"):
            tag_name = os.environ.get("TAG_NAME")
        else:
            print("metric lead_time requires TAG_NAME", file=sys.stderr)
            return

    run = mk_run(repo_path)
    deployment_data = list(
        fetch_tags_and_author_dates(
            run, partial(fnmatch, pat=deploy_tag_pattern), start_date
        )
    )
    deployment_data_filtered = next(
        filter(lambda x: x[0] == tag_name, deployment_data), []
    )
    if deployment_data_filtered:
        lead_time = datetime.datetime.now().timestamp() - deployment_data_filtered[1]
        print(f"lead_time: {lead_time:.6f}")


if __name__ == "__main__":
    lead_time()
    pipeline_time()
