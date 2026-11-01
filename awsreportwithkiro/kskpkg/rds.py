####################################################################################################
#
# Purpose   : get RDS db clusters (REGIONAL)
# Source    : rds.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / rds.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_db_clusters(ctx) -> list[dict]:
    results = []
    try:
        rds = ctx.get_client("rds")
        for c in paginate(rds, "describe_db_clusters", "DBClusters"):
            sgs = [g.get("VpcSecurityGroupId", " ") for g in c.get("VpcSecurityGroups", [])]
            results.append({
                "DBClusterIdentifier": c.get("DBClusterIdentifier", " "),
                "Engine": c.get("Engine", " "),
                "EngineVersion": c.get("EngineVersion", " "),
                "Status": c.get("Status", " "),
                "Endpoint": c.get("Endpoint", " "),
                "ReaderEndpoint": c.get("ReaderEndpoint", " "),
                "MultiAZ": c.get("MultiAZ", " "),
                "StorageEncrypted": c.get("StorageEncrypted", " "),
                "KmsKeyId": c.get("KmsKeyId", " "),
                "KmsKeyAlias": "",
                "VpcSecurityGroups": sgs if sgs else " ",
                "VpcSecurityGroupTName": "",
            })
        if not results:
            results.append({"DBClusterIdentifier": " ", "Engine": " ", "EngineVersion": " ", "Status": " ",
                            "Endpoint": " ", "ReaderEndpoint": " ", "MultiAZ": " ", "StorageEncrypted": " ",
                            "KmsKeyId": " ", "KmsKeyAlias": " ", "VpcSecurityGroups": " ",
                            "VpcSecurityGroupTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("rds.describe_db_clusters(),region[%s],%s", ctx.region, err)
        results = [{"DBClusterIdentifier": "ERROR CHECK", "Engine": "ERROR CHECK", "EngineVersion": "ERROR CHECK",
                    "Status": "ERROR CHECK", "Endpoint": "ERROR CHECK", "ReaderEndpoint": "ERROR CHECK",
                    "MultiAZ": "ERROR CHECK", "StorageEncrypted": "ERROR CHECK", "KmsKeyId": "ERROR CHECK",
                    "KmsKeyAlias": "ERROR CHECK", "VpcSecurityGroups": "ERROR CHECK",
                    "VpcSecurityGroupTName": "ERROR CHECK"}]
    return results
