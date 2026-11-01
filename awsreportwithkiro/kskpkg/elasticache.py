####################################################################################################
#
# Purpose   : get ElastiCache cache clusters (REGIONAL)
# Source    : elasticache.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / elasticache.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_cache_clusters(ctx) -> list[dict]:
    results = []
    try:
        ec = ctx.get_client("elasticache")
        for c in paginate(ec, "describe_cache_clusters", "CacheClusters"):
            sgs = [g.get("SecurityGroupId", " ") for g in c.get("SecurityGroups", [])]
            results.append({
                "CacheClusterId": c.get("CacheClusterId", " "),
                "Engine": c.get("Engine", " "),
                "EngineVersion": c.get("EngineVersion", " "),
                "CacheClusterStatus": c.get("CacheClusterStatus", " "),
                "CacheNodeType": c.get("CacheNodeType", " "),
                "NumCacheNodes": c.get("NumCacheNodes", " "),
                "PreferredAvailabilityZone": c.get("PreferredAvailabilityZone", " "),
                "CacheSecurityGroup": " ",
                "SecurityGroup": sgs[0] if sgs else " ",
                "SecurityGroups": sgs if sgs else " ",
                "SecurityGroupTName": "",
                "AtRestEncryptionEnabled": c.get("AtRestEncryptionEnabled", " "),
            })
        if not results:
            results.append({"CacheClusterId": " ", "Engine": " ", "EngineVersion": " ",
                            "CacheClusterStatus": " ", "CacheNodeType": " ", "NumCacheNodes": " ",
                            "PreferredAvailabilityZone": " ", "CacheSecurityGroup": " ",
                            "SecurityGroup": " ", "SecurityGroups": " ", "SecurityGroupTName": " ",
                            "AtRestEncryptionEnabled": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("elasticache.describe_cache_clusters(),region[%s],%s", ctx.region, err)
        results = [{"CacheClusterId": "ERROR CHECK", "Engine": "ERROR CHECK", "EngineVersion": "ERROR CHECK",
                    "CacheClusterStatus": "ERROR CHECK", "CacheNodeType": "ERROR CHECK",
                    "NumCacheNodes": "ERROR CHECK", "PreferredAvailabilityZone": "ERROR CHECK",
                    "CacheSecurityGroup": "ERROR CHECK", "SecurityGroup": "ERROR CHECK",
                    "SecurityGroups": "ERROR CHECK", "SecurityGroupTName": "ERROR CHECK",
                    "AtRestEncryptionEnabled": "ERROR CHECK"}]
    return results
