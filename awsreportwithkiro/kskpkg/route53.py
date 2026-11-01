####################################################################################################
#
# Purpose   : get Route53 hosted zones and resource record sets (GLOBAL)
# Source    : route53.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / route53.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_hosted_zones(ctx) -> list[dict]:
    results = []
    try:
        r53 = ctx.get_client("route53")
        for host in paginate(r53, "list_hosted_zones", "HostedZones"):
            config = host.get("Config", {})
            results.append({
                "Id": host["Id"],
                "Name": host.get("Name", " "),
                "Comment": config.get("Comment", " "),
                "Type": "Private" if config.get("PrivateZone") else "Public",
                "ResourceRecordSetCount": host.get("ResourceRecordSetCount", " "),
                "CallerReference": host.get("CallerReference", " "),
            })
        if not results:
            results.append({"Id": " ", "Name": " ", "Comment": " ", "Type": " ",
                            "ResourceRecordSetCount": " ", "CallerReference": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("route53.list_hosted_zones(),%s", err)
        results = [{"Id": "ERROR CHECK", "Name": "ERROR CHECK", "Comment": "ERROR CHECK",
                    "Type": "ERROR CHECK", "ResourceRecordSetCount": "ERROR CHECK",
                    "CallerReference": "ERROR CHECK"}]
    return results


def list_resource_record_sets(ctx) -> list[dict]:
    results = []
    zones_df = ctx.deps.get("route53")
    zone_ids = []
    if zones_df is not None and not zones_df.empty and "Id" in zones_df.columns:
        zone_ids = [z for z in zones_df["Id"].tolist() if z and z != " "]
    try:
        r53 = ctx.get_client("route53")
        for zid in zone_ids:
            short = zid.split("/")[-1]
            for rec in paginate(r53, "list_resource_record_sets", "ResourceRecordSets",
                                HostedZoneId=short):
                values = [rr.get("Value", " ") for rr in rec.get("ResourceRecords", [])]
                alias = rec.get("AliasTarget", {})
                results.append({
                    "HostedZoneId": zid,
                    "Name": rec.get("Name", " "),
                    "Type": rec.get("Type", " "),
                    "ResourceRecords": values if values else " ",
                    "AliasTarget": alias.get("DNSName", " "),
                    "EvaluateTargetHealth": alias.get("EvaluateTargetHealth", " "),
                    "SetIdentifier": rec.get("SetIdentifier", " "),
                    "TTL": rec.get("TTL", " "),
                })
        if not results:
            results.append({"HostedZoneId": " ", "Name": " ", "Type": " ", "ResourceRecords": " ",
                            "AliasTarget": " ", "EvaluateTargetHealth": " ", "SetIdentifier": " ", "TTL": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("route53.list_resource_record_sets(),%s", err)
        results = [{"HostedZoneId": "ERROR CHECK", "Name": "ERROR CHECK", "Type": "ERROR CHECK",
                    "ResourceRecords": "ERROR CHECK", "AliasTarget": "ERROR CHECK",
                    "EvaluateTargetHealth": "ERROR CHECK", "SetIdentifier": "ERROR CHECK", "TTL": "ERROR CHECK"}]
    return results
