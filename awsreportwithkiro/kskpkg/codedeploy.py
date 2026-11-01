####################################################################################################
#
# Purpose   : get CodeDeploy applications and deployments (REGIONAL)
# Source    : codedeploy.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / codedeploy.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codedeploy.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_applications(ctx) -> list[dict]:
    results = []
    try:
        cd = ctx.get_client("codedeploy")
        for app in paginate(cd, "list_applications", "applications"):
            results.append({"ApplicationName": app})
        if not results:
            results.append({"ApplicationName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("codedeploy.list_applications(),region[%s],%s", ctx.region, err)
        results = [{"ApplicationName": "ERROR CHECK"}]
    return results


def list_deployments(ctx) -> list[dict]:
    results = []
    try:
        cd = ctx.get_client("codedeploy")
        for dep in paginate(cd, "list_deployments", "deployments"):
            results.append({"DeploymentId": dep})
        if not results:
            results.append({"DeploymentId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("codedeploy.list_deployments(),region[%s],%s", ctx.region, err)
        results = [{"DeploymentId": "ERROR CHECK"}]
    return results
