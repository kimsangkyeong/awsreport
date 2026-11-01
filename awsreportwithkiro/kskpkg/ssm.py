####################################################################################################
#
# Purpose   : get SSM Parameter Store parameters (REGIONAL)
# Source    : ssm.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / ssm.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_parameters(ctx) -> list[dict]:
    results = []
    try:
        ssm = ctx.get_client("ssm")
        for p in paginate(ssm, "describe_parameters", "Parameters"):
            results.append({
                "Name": p.get("Name", " "),
                "Type": p.get("Type", " "),
                "Tier": p.get("Tier", " "),
                "Version": p.get("Version", " "),
                "DataType": p.get("DataType", " "),
                "LastModifiedDate": p.get("LastModifiedDate").strftime("%Y-%m-%d %H:%M")
                if p.get("LastModifiedDate") else " ",
                "Description": p.get("Description", " "),
            })
        if not results:
            results.append({"Name": " ", "Type": " ", "Tier": " ", "Version": " ",
                            "DataType": " ", "LastModifiedDate": " ", "Description": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ssm.describe_parameters(),region[%s],%s", ctx.region, err)
        results = [{"Name": "ERROR CHECK", "Type": "ERROR CHECK", "Tier": "ERROR CHECK", "Version": "ERROR CHECK",
                    "DataType": "ERROR CHECK", "LastModifiedDate": "ERROR CHECK", "Description": "ERROR CHECK"}]
    return results
