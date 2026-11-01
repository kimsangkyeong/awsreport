####################################################################################################
#
# Purpose   : get Redshift clusters (REGIONAL)
# Source    : redshift.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / redshift.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_clusters(ctx) -> list[dict]:
    results = []
    try:
        rs = ctx.get_client("redshift")
        for c in paginate(rs, "describe_clusters", "Clusters"):
            sgs = [g.get("VpcSecurityGroupId", " ") for g in c.get("VpcSecurityGroups", [])]
            results.append({
                "ClusterIdentifier": c.get("ClusterIdentifier", " "),
                "NodeType": c.get("NodeType", " "),
                "ClusterStatus": c.get("ClusterStatus", " "),
                "NumberOfNodes": c.get("NumberOfNodes", " "),
                "DBName": c.get("DBName", " "),
                "VpcId": c.get("VpcId", " "),
                "VpcTName": "",
                "VpcSecurityGroups": sgs if sgs else " ",
                "VpcSecurityGroupTName": "",
                "Encrypted": c.get("Encrypted", " "),
                "KmsKeyId": c.get("KmsKeyId", " "),
                "KmsKeyAlias": "",
                "Endpoint": c.get("Endpoint", {}).get("Address", " "),
            })
        if not results:
            results.append({"ClusterIdentifier": " ", "NodeType": " ", "ClusterStatus": " ",
                            "NumberOfNodes": " ", "DBName": " ", "VpcId": " ", "VpcTName": " ",
                            "VpcSecurityGroups": " ", "VpcSecurityGroupTName": " ",
                            "Encrypted": " ", "KmsKeyId": " ", "KmsKeyAlias": " ", "Endpoint": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("redshift.describe_clusters(),region[%s],%s", ctx.region, err)
        results = [{"ClusterIdentifier": "ERROR CHECK", "NodeType": "ERROR CHECK", "ClusterStatus": "ERROR CHECK",
                    "NumberOfNodes": "ERROR CHECK", "DBName": "ERROR CHECK", "VpcId": "ERROR CHECK",
                    "VpcTName": "ERROR CHECK", "VpcSecurityGroups": "ERROR CHECK",
                    "VpcSecurityGroupTName": "ERROR CHECK", "Encrypted": "ERROR CHECK", "KmsKeyId": "ERROR CHECK",
                    "KmsKeyAlias": "ERROR CHECK", "Endpoint": "ERROR CHECK"}]
    return results
