####################################################################################################
#
# Purpose   : get ECS clusters and services (REGIONAL)
# Source    : ecs.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / ecs.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_clusters(ctx) -> list[dict]:
    results = []
    try:
        ecs = ctx.get_client("ecs")
        arns = list(paginate(ecs, "list_clusters", "clusterArns"))
        clusters = []
        if arns:
            clusters = ecs.describe_clusters(clusters=arns).get("clusters", [])
        for c in clusters:
            results.append({
                "ClusterArn": c.get("clusterArn", " "),
                "ECSClusterName": c.get("clusterName", " "),
                "Status": c.get("status", " "),
                "RegisteredContainerInstancesCount": c.get("registeredContainerInstancesCount", " "),
                "RunningTasksCount": c.get("runningTasksCount", " "),
                "ActiveServicesCount": c.get("activeServicesCount", " "),
            })
        if not results:
            results.append({"ClusterArn": " ", "ECSClusterName": " ", "Status": " ",
                            "RegisteredContainerInstancesCount": " ", "RunningTasksCount": " ",
                            "ActiveServicesCount": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ecs.list_clusters(),region[%s],%s", ctx.region, err)
        results = [{"ClusterArn": "ERROR CHECK", "ECSClusterName": "ERROR CHECK", "Status": "ERROR CHECK",
                    "RegisteredContainerInstancesCount": "ERROR CHECK", "RunningTasksCount": "ERROR CHECK",
                    "ActiveServicesCount": "ERROR CHECK"}]
    return results


def list_services(ctx) -> list[dict]:
    results = []
    clusters_df = ctx.deps.get("ecs")
    cluster_arns = []
    if clusters_df is not None and not clusters_df.empty and "ClusterArn" in clusters_df.columns:
        cluster_arns = [a for a in clusters_df["ClusterArn"].tolist() if a and a != " "]
    try:
        ecs = ctx.get_client("ecs")
        for cluster_arn in cluster_arns:
            svc_arns = list(paginate(ecs, "list_services", "serviceArns", cluster=cluster_arn))
            # describe_services 는 10개 단위
            for i in range(0, len(svc_arns), 10):
                batch = svc_arns[i:i + 10]
                services = ecs.describe_services(cluster=cluster_arn, services=batch).get("services", [])
                for s in services:
                    net = s.get("networkConfiguration", {}).get("awsvpcConfiguration", {})
                    subnets = net.get("subnets", [])
                    sgs = net.get("securityGroups", [])
                    results.append({
                        "ClusterArn": cluster_arn,
                        "ECSClusterName": "",
                        "ServiceName": s.get("serviceName", " "),
                        "Status": s.get("status", " "),
                        "LaunchType": s.get("launchType", " "),
                        "DesiredCount": s.get("desiredCount", " "),
                        "RunningCount": s.get("runningCount", " "),
                        "TaskDefinition": s.get("taskDefinition", " "),
                        "SubnetId": subnets[0] if subnets else " ",
                        "SubnetTName": "",
                        "SecurityGroups": sgs if sgs else " ",
                        "SecurityGroupTName": "",
                    })
        if not results:
            results.append({"ClusterArn": " ", "ECSClusterName": " ", "ServiceName": " ", "Status": " ",
                            "LaunchType": " ", "DesiredCount": " ", "RunningCount": " ",
                            "TaskDefinition": " ", "SubnetId": " ", "SubnetTName": " ",
                            "SecurityGroups": " ", "SecurityGroupTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ecs.list_services(),region[%s],%s", ctx.region, err)
        results = [{"ClusterArn": "ERROR CHECK", "ECSClusterName": "ERROR CHECK", "ServiceName": "ERROR CHECK",
                    "Status": "ERROR CHECK", "LaunchType": "ERROR CHECK", "DesiredCount": "ERROR CHECK",
                    "RunningCount": "ERROR CHECK", "TaskDefinition": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                    "SubnetTName": "ERROR CHECK", "SecurityGroups": "ERROR CHECK", "SecurityGroupTName": "ERROR CHECK"}]
    return results
