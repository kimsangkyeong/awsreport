####################################################################################################
#
# Purpose   : get CodePipeline pipelines (REGIONAL)
# Source    : codepipeline.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / codepipeline.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_pipelines(ctx) -> list[dict]:
    results = []
    try:
        cp = ctx.get_client("codepipeline")
        for p in paginate(cp, "list_pipelines", "pipelines"):
            results.append({
                "Name": p.get("name", " "),
                "Version": p.get("version", " "),
                "Created": p.get("created").strftime("%Y-%m-%d %H:%M") if p.get("created") else " ",
                "Updated": p.get("updated").strftime("%Y-%m-%d %H:%M") if p.get("updated") else " ",
            })
        if not results:
            results.append({"Name": " ", "Version": " ", "Created": " ", "Updated": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("codepipeline.list_pipelines(),region[%s],%s", ctx.region, err)
        results = [{"Name": "ERROR CHECK", "Version": "ERROR CHECK", "Created": "ERROR CHECK",
                    "Updated": "ERROR CHECK"}]
    return results
