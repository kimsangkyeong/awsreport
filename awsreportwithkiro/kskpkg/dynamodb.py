####################################################################################################
#
# Purpose   : get DynamoDB tables and global tables (REGIONAL)
# Source    : dynamodb.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / dynamodb.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_tables(ctx) -> list[dict]:
    results = []
    try:
        ddb = ctx.get_client("dynamodb")
        for name in paginate(ddb, "list_tables", "TableNames"):
            try:
                t = ddb.describe_table(TableName=name).get("Table", {})
            except Exception:  # noqa: BLE001
                t = {"TableName": name}
            results.append({
                "TableName": t.get("TableName", name),
                "TableStatus": t.get("TableStatus", " "),
                "ItemCount": t.get("ItemCount", " "),
                "TableSizeBytes": t.get("TableSizeBytes", " "),
                "BillingMode": t.get("BillingModeSummary", {}).get("BillingMode", " "),
                "TableArn": t.get("TableArn", " "),
            })
        if not results:
            results.append({"TableName": " ", "TableStatus": " ", "ItemCount": " ",
                            "TableSizeBytes": " ", "BillingMode": " ", "TableArn": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("dynamodb.list_tables(),region[%s],%s", ctx.region, err)
        results = [{"TableName": "ERROR CHECK", "TableStatus": "ERROR CHECK", "ItemCount": "ERROR CHECK",
                    "TableSizeBytes": "ERROR CHECK", "BillingMode": "ERROR CHECK", "TableArn": "ERROR CHECK"}]
    return results


def list_global_tables(ctx) -> list[dict]:
    results = []
    try:
        ddb = ctx.get_client("dynamodb")
        # list_global_tables 는 paginator 미지원 → ExclusiveStartGlobalTableName 수동 루프
        last = None
        gtables = []
        while True:
            kwargs = {"ExclusiveStartGlobalTableName": last} if last else {}
            resp = ddb.list_global_tables(**kwargs)
            batch = resp.get("GlobalTables", [])
            gtables.extend(batch)
            last = resp.get("LastEvaluatedGlobalTableName")
            if not last:
                break
        for gt in gtables:
            regions = [rg.get("RegionName", " ") for rg in gt.get("ReplicationGroup", [])]
            results.append({
                "GlobalTableName": gt.get("GlobalTableName", " "),
                "ReplicationRegions": regions if regions else " ",
            })
        if not results:
            results.append({"GlobalTableName": " ", "ReplicationRegions": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("dynamodb.list_global_tables(),region[%s],%s", ctx.region, err)
        results = [{"GlobalTableName": "ERROR CHECK", "ReplicationRegions": "ERROR CHECK"}]
    return results
