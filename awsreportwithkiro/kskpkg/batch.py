####################################################################################################
#
# Purpose   : get AWS Batch compute environments / job queues / job definitions (REGIONAL)
# Source    : batch.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/batch.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_compute_environments(ctx) -> list[dict]:
    """Batch 컴퓨트 환경. Subnet/SecurityGroup 식별성 위해 TName 자리 둠."""
    results = []
    try:
        batch = ctx.get_client("batch")
        for ce in paginate(batch, "describe_compute_environments", "computeEnvironments"):
            cr = ce.get("computeResources", {}) or {}
            subnets = cr.get("subnets", []) or []
            sgs = cr.get("securityGroupIds", []) or []
            results.append({
                "ComputeEnvironmentName": ce.get("computeEnvironmentName", " "),
                "ComputeEnvironmentArn": ce.get("computeEnvironmentArn", " "),
                "Type": ce.get("type", " "),
                "State": ce.get("state", " "),
                "Status": ce.get("status", " "),
                "ContainerOrchestrationType": ce.get("containerOrchestrationType", " "),
                "ComputeType": cr.get("type", " "),
                "AllocationStrategy": cr.get("allocationStrategy", " "),
                "MinvCpus": cr.get("minvCpus", " "),
                "MaxvCpus": cr.get("maxvCpus", " "),
                "DesiredvCpus": cr.get("desiredvCpus", " "),
                "InstanceTypes": cr.get("instanceTypes", " ") or " ",
                "SubnetId": subnets[0] if subnets else " ",
                "SubnetTName": "",
                "Subnets": subnets if subnets else " ",
                "SecurityGroupIds": sgs if sgs else " ",
                "SecurityGroupTName": "",
                "EcsClusterArn": ce.get("ecsClusterArn", " "),
                "ServiceRole": ce.get("serviceRole", " "),
            })
        if not results:
            results.append({"ComputeEnvironmentName": " ", "ComputeEnvironmentArn": " ", "Type": " ",
                            "State": " ", "Status": " ", "ContainerOrchestrationType": " ", "ComputeType": " ",
                            "AllocationStrategy": " ", "MinvCpus": " ", "MaxvCpus": " ", "DesiredvCpus": " ",
                            "InstanceTypes": " ", "SubnetId": " ", "SubnetTName": " ", "Subnets": " ",
                            "SecurityGroupIds": " ", "SecurityGroupTName": " ", "EcsClusterArn": " ",
                            "ServiceRole": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("batch.describe_compute_environments(),region[%s],%s", ctx.region, err)
        results = [{"ComputeEnvironmentName": "ERROR CHECK", "ComputeEnvironmentArn": "ERROR CHECK",
                    "Type": "ERROR CHECK", "State": "ERROR CHECK", "Status": "ERROR CHECK",
                    "ContainerOrchestrationType": "ERROR CHECK", "ComputeType": "ERROR CHECK",
                    "AllocationStrategy": "ERROR CHECK", "MinvCpus": "ERROR CHECK", "MaxvCpus": "ERROR CHECK",
                    "DesiredvCpus": "ERROR CHECK", "InstanceTypes": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                    "SubnetTName": "ERROR CHECK", "Subnets": "ERROR CHECK", "SecurityGroupIds": "ERROR CHECK",
                    "SecurityGroupTName": "ERROR CHECK", "EcsClusterArn": "ERROR CHECK", "ServiceRole": "ERROR CHECK"}]
    return results


def describe_job_queues(ctx) -> list[dict]:
    """Batch 작업 큐. 연결된 컴퓨트 환경(우선순위 순)도 함께 표시."""
    results = []
    try:
        batch = ctx.get_client("batch")
        for jq in paginate(batch, "describe_job_queues", "jobQueues"):
            ce_order = [c.get("computeEnvironment", " ") for c in jq.get("computeEnvironmentOrder", [])]
            results.append({
                "JobQueueName": jq.get("jobQueueName", " "),
                "JobQueueArn": jq.get("jobQueueArn", " "),
                "State": jq.get("state", " "),
                "Status": jq.get("status", " "),
                "Priority": jq.get("priority", " "),
                "JobQueueType": jq.get("jobQueueType", " "),
                "SchedulingPolicyArn": jq.get("schedulingPolicyArn", " "),
                "ComputeEnvironmentOrder": ce_order if ce_order else " ",
            })
        if not results:
            results.append({"JobQueueName": " ", "JobQueueArn": " ", "State": " ", "Status": " ",
                            "Priority": " ", "JobQueueType": " ", "SchedulingPolicyArn": " ",
                            "ComputeEnvironmentOrder": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("batch.describe_job_queues(),region[%s],%s", ctx.region, err)
        results = [{"JobQueueName": "ERROR CHECK", "JobQueueArn": "ERROR CHECK", "State": "ERROR CHECK",
                    "Status": "ERROR CHECK", "Priority": "ERROR CHECK", "JobQueueType": "ERROR CHECK",
                    "SchedulingPolicyArn": "ERROR CHECK", "ComputeEnvironmentOrder": "ERROR CHECK"}]
    return results


def describe_job_definitions(ctx) -> list[dict]:
    """Batch 작업 정의 (ACTIVE revision)."""
    results = []
    try:
        batch = ctx.get_client("batch")
        # ACTIVE 상태만 조회 (비활성 revision 폭주 방지)
        for jd in paginate(batch, "describe_job_definitions", "jobDefinitions", status="ACTIVE"):
            cp = jd.get("containerProperties", {}) or {}
            results.append({
                "JobDefinitionName": jd.get("jobDefinitionName", " "),
                "JobDefinitionArn": jd.get("jobDefinitionArn", " "),
                "Revision": jd.get("revision", " "),
                "Status": jd.get("status", " "),
                "Type": jd.get("type", " "),
                "PlatformCapabilities": jd.get("platformCapabilities", " ") or " ",
                "ContainerImage": cp.get("image", " "),
                "vCpus": cp.get("vcpus", " "),
                "Memory": cp.get("memory", " "),
                "JobRoleArn": cp.get("jobRoleArn", " "),
                "ExecutionRoleArn": cp.get("executionRoleArn", " "),
            })
        if not results:
            results.append({"JobDefinitionName": " ", "JobDefinitionArn": " ", "Revision": " ", "Status": " ",
                            "Type": " ", "PlatformCapabilities": " ", "ContainerImage": " ", "vCpus": " ",
                            "Memory": " ", "JobRoleArn": " ", "ExecutionRoleArn": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("batch.describe_job_definitions(),region[%s],%s", ctx.region, err)
        results = [{"JobDefinitionName": "ERROR CHECK", "JobDefinitionArn": "ERROR CHECK", "Revision": "ERROR CHECK",
                    "Status": "ERROR CHECK", "Type": "ERROR CHECK", "PlatformCapabilities": "ERROR CHECK",
                    "ContainerImage": "ERROR CHECK", "vCpus": "ERROR CHECK", "Memory": "ERROR CHECK",
                    "JobRoleArn": "ERROR CHECK", "ExecutionRoleArn": "ERROR CHECK"}]
    return results
