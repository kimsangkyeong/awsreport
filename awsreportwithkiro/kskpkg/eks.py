####################################################################################################
#
# Purpose   : get EKS clusters + addons / nodegroups / fargate profiles (REGIONAL)
# Source    : eks.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / eks.py, ctx-based)
#  1.1      2026.11.01     add addons, nodegroups, fargate profiles
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_clusters(ctx) -> list[dict]:
    results = []
    try:
        eks = ctx.get_client("eks")
        for name in paginate(eks, "list_clusters", "clusters"):
            try:
                c = eks.describe_cluster(name=name).get("cluster", {})
            except Exception:  # noqa: BLE001
                c = {"name": name}
            vpc_cfg = c.get("resourcesVpcConfig", {})
            subnets = vpc_cfg.get("subnetIds", [])
            enc = (c.get("encryptionConfig") or [{}])[0].get("provider", {})
            results.append({
                "ClusterName": c.get("name", name),
                "Status": c.get("status", " "),
                "Version": c.get("version", " "),
                "Endpoint": c.get("endpoint", " "),
                "VpcId": vpc_cfg.get("vpcId", " "),
                "VpcTName": "",
                "SubnetId": subnets[0] if subnets else " ",
                "SubnetTName": "",
                "Subnets": subnets if subnets else " ",
                "ClusterSecurityGroupId": vpc_cfg.get("clusterSecurityGroupId", " "),
                "ClusterSecurityGroupTName": "",
                "EncryptKeyArn": enc.get("keyArn", " "),
                "EncryptKeyAlias": "",
            })
        if not results:
            results.append({"ClusterName": " ", "Status": " ", "Version": " ", "Endpoint": " ",
                            "VpcId": " ", "VpcTName": " ", "SubnetId": " ", "SubnetTName": " ",
                            "Subnets": " ", "ClusterSecurityGroupId": " ", "ClusterSecurityGroupTName": " ",
                            "EncryptKeyArn": " ", "EncryptKeyAlias": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("eks.list_clusters(),region[%s],%s", ctx.region, err)
        results = [{"ClusterName": "ERROR CHECK", "Status": "ERROR CHECK", "Version": "ERROR CHECK",
                    "Endpoint": "ERROR CHECK", "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK",
                    "SubnetId": "ERROR CHECK", "SubnetTName": "ERROR CHECK", "Subnets": "ERROR CHECK",
                    "ClusterSecurityGroupId": "ERROR CHECK", "ClusterSecurityGroupTName": "ERROR CHECK",
                    "EncryptKeyArn": "ERROR CHECK", "EncryptKeyAlias": "ERROR CHECK"}]
    return results


def _cluster_names(ctx) -> list[str]:
    """deps['eks'] DataFrame 에서 클러스터 이름 목록 추출."""
    df = ctx.deps.get("eks")
    names = []
    if df is not None and not df.empty and "ClusterName" in df.columns:
        for n in df["ClusterName"].tolist():
            if n and n not in (" ", "ERROR CHECK"):
                names.append(n)
    return names


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else " "


def list_addons(ctx) -> list[dict]:
    """EKS 클러스터별 addon (vpc-cni/coredns/kube-proxy/ebs-csi-driver 등)."""
    results = []
    try:
        eks = ctx.get_client("eks")
        for cluster in _cluster_names(ctx):
            for addon_name in paginate(eks, "list_addons", "addons", clusterName=cluster):
                try:
                    a = eks.describe_addon(clusterName=cluster, addonName=addon_name).get("addon", {})
                except Exception:  # noqa: BLE001
                    a = {"addonName": addon_name, "clusterName": cluster}
                health_issues = a.get("health", {}).get("issues", [])
                results.append({
                    "ClusterName": a.get("clusterName", cluster),
                    "AddonName": a.get("addonName", addon_name),
                    "AddonVersion": a.get("addonVersion", " "),
                    "Status": a.get("status", " "),
                    "ServiceAccountRoleArn": a.get("serviceAccountRoleArn", " "),
                    "Publisher": a.get("publisher", " "),
                    "Owner": a.get("owner", " "),
                    "HealthIssues": [i.get("code", " ") for i in health_issues] if health_issues else " ",
                    "CreatedAt": _fmt(a.get("createdAt")),
                    "ModifiedAt": _fmt(a.get("modifiedAt")),
                })
        if not results:
            results.append({"ClusterName": " ", "AddonName": " ", "AddonVersion": " ", "Status": " ",
                            "ServiceAccountRoleArn": " ", "Publisher": " ", "Owner": " ",
                            "HealthIssues": " ", "CreatedAt": " ", "ModifiedAt": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("eks.list_addons(),region[%s],%s", ctx.region, err)
        results = [{"ClusterName": "ERROR CHECK", "AddonName": "ERROR CHECK", "AddonVersion": "ERROR CHECK",
                    "Status": "ERROR CHECK", "ServiceAccountRoleArn": "ERROR CHECK", "Publisher": "ERROR CHECK",
                    "Owner": "ERROR CHECK", "HealthIssues": "ERROR CHECK", "CreatedAt": "ERROR CHECK",
                    "ModifiedAt": "ERROR CHECK"}]
    return results


def list_nodegroups(ctx) -> list[dict]:
    """EKS 관리형 노드 그룹. Subnet/SecurityGroup 식별성 위해 TName 자리 둠."""
    results = []
    try:
        eks = ctx.get_client("eks")
        for cluster in _cluster_names(ctx):
            for ng_name in paginate(eks, "list_nodegroups", "nodegroups", clusterName=cluster):
                try:
                    n = eks.describe_nodegroup(clusterName=cluster, nodegroupName=ng_name).get("nodegroup", {})
                except Exception:  # noqa: BLE001
                    n = {"nodegroupName": ng_name, "clusterName": cluster}
                scaling = n.get("scalingConfig", {}) or {}
                subnets = n.get("subnets", []) or []
                remote_sg = n.get("resources", {}).get("remoteAccessSecurityGroup", " ")
                asgs = [g.get("name", " ") for g in n.get("resources", {}).get("autoScalingGroups", [])]
                results.append({
                    "ClusterName": n.get("clusterName", cluster),
                    "NodegroupName": n.get("nodegroupName", ng_name),
                    "Status": n.get("status", " "),
                    "CapacityType": n.get("capacityType", " "),
                    "InstanceTypes": n.get("instanceTypes", " ") or " ",
                    "AmiType": n.get("amiType", " "),
                    "Version": n.get("version", " "),
                    "MinSize": scaling.get("minSize", " "),
                    "MaxSize": scaling.get("maxSize", " "),
                    "DesiredSize": scaling.get("desiredSize", " "),
                    "DiskSize": n.get("diskSize", " "),
                    "SubnetId": subnets[0] if subnets else " ",
                    "SubnetTName": "",
                    "Subnets": subnets if subnets else " ",
                    "RemoteAccessSecurityGroupId": remote_sg,
                    "RemoteAccessSecurityGroupTName": "",
                    "AutoScalingGroups": asgs if asgs else " ",
                    "NodeRole": n.get("nodeRole", " "),
                })
        if not results:
            results.append({"ClusterName": " ", "NodegroupName": " ", "Status": " ", "CapacityType": " ",
                            "InstanceTypes": " ", "AmiType": " ", "Version": " ", "MinSize": " ",
                            "MaxSize": " ", "DesiredSize": " ", "DiskSize": " ", "SubnetId": " ",
                            "SubnetTName": " ", "Subnets": " ", "RemoteAccessSecurityGroupId": " ",
                            "RemoteAccessSecurityGroupTName": " ", "AutoScalingGroups": " ", "NodeRole": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("eks.list_nodegroups(),region[%s],%s", ctx.region, err)
        results = [{"ClusterName": "ERROR CHECK", "NodegroupName": "ERROR CHECK", "Status": "ERROR CHECK",
                    "CapacityType": "ERROR CHECK", "InstanceTypes": "ERROR CHECK", "AmiType": "ERROR CHECK",
                    "Version": "ERROR CHECK", "MinSize": "ERROR CHECK", "MaxSize": "ERROR CHECK",
                    "DesiredSize": "ERROR CHECK", "DiskSize": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                    "SubnetTName": "ERROR CHECK", "Subnets": "ERROR CHECK",
                    "RemoteAccessSecurityGroupId": "ERROR CHECK", "RemoteAccessSecurityGroupTName": "ERROR CHECK",
                    "AutoScalingGroups": "ERROR CHECK", "NodeRole": "ERROR CHECK"}]
    return results


def list_fargate_profiles(ctx) -> list[dict]:
    """EKS Fargate 프로파일. Subnet 식별성 위해 TName 자리 둠."""
    results = []
    try:
        eks = ctx.get_client("eks")
        for cluster in _cluster_names(ctx):
            for fp_name in paginate(eks, "list_fargate_profiles", "fargateProfileNames", clusterName=cluster):
                try:
                    f = eks.describe_fargate_profile(
                        clusterName=cluster, fargateProfileName=fp_name).get("fargateProfile", {})
                except Exception:  # noqa: BLE001
                    f = {"fargateProfileName": fp_name, "clusterName": cluster}
                subnets = f.get("subnets", []) or []
                selectors = []
                for sel in f.get("selectors", []):
                    selectors.append({"namespace": sel.get("namespace", " "), "labels": sel.get("labels", {})})
                results.append({
                    "ClusterName": f.get("clusterName", cluster),
                    "FargateProfileName": f.get("fargateProfileName", fp_name),
                    "Status": f.get("status", " "),
                    "PodExecutionRoleArn": f.get("podExecutionRoleArn", " "),
                    "SubnetId": subnets[0] if subnets else " ",
                    "SubnetTName": "",
                    "Subnets": subnets if subnets else " ",
                    "Selectors": selectors if selectors else " ",
                    "CreatedAt": _fmt(f.get("createdAt")),
                })
        if not results:
            results.append({"ClusterName": " ", "FargateProfileName": " ", "Status": " ",
                            "PodExecutionRoleArn": " ", "SubnetId": " ", "SubnetTName": " ",
                            "Subnets": " ", "Selectors": " ", "CreatedAt": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("eks.list_fargate_profiles(),region[%s],%s", ctx.region, err)
        results = [{"ClusterName": "ERROR CHECK", "FargateProfileName": "ERROR CHECK", "Status": "ERROR CHECK",
                    "PodExecutionRoleArn": "ERROR CHECK", "SubnetId": "ERROR CHECK", "SubnetTName": "ERROR CHECK",
                    "Subnets": "ERROR CHECK", "Selectors": "ERROR CHECK", "CreatedAt": "ERROR CHECK"}]
    return results
