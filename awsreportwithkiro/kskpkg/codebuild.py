####################################################################################################
#
# Purpose   : get CodeBuild projects (REGIONAL)
# Source    : codebuild.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / codebuild.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_projects(ctx) -> list[dict]:
    results = []
    try:
        cb = ctx.get_client("codebuild")
        names = list(paginate(cb, "list_projects", "projects"))
        projects = []
        if names:
            for i in range(0, len(names), 100):
                batch = names[i:i + 100]
                projects.extend(cb.batch_get_projects(names=batch).get("projects", []))
        for p in projects:
            vpc = p.get("vpcConfig", {})
            subnets = vpc.get("subnets", [])
            sgs = vpc.get("securityGroupIds", [])
            results.append({
                "ProjectName": p.get("name", " "),
                "Description": p.get("description", " "),
                "EnvironmentType": p.get("environment", {}).get("type", " "),
                "Image": p.get("environment", {}).get("image", " "),
                "VpcId": vpc.get("vpcId", " "),
                "VpcTName": "",
                "Subnets": subnets if subnets else " ",
                "SubnetTName": "",
                "SecurityGroup": sgs if sgs else " ",
                "SecurityGroupTName": "",
            })
        if not results:
            results.append({"ProjectName": " ", "Description": " ", "EnvironmentType": " ", "Image": " ",
                            "VpcId": " ", "VpcTName": " ", "Subnets": " ", "SubnetTName": " ",
                            "SecurityGroup": " ", "SecurityGroupTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("codebuild.list_projects(),region[%s],%s", ctx.region, err)
        results = [{"ProjectName": "ERROR CHECK", "Description": "ERROR CHECK", "EnvironmentType": "ERROR CHECK",
                    "Image": "ERROR CHECK", "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK",
                    "Subnets": "ERROR CHECK", "SubnetTName": "ERROR CHECK", "SecurityGroup": "ERROR CHECK",
                    "SecurityGroupTName": "ERROR CHECK"}]
    return results
