####################################################################################################
#
# Purpose   : get Athena data catalogs (REGIONAL)
# Source    : athena.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / athena.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/athena.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_data_catalogs(ctx) -> list[dict]:
    results = []
    try:
        athena = ctx.get_client("athena")
        for cat in paginate(athena, "list_data_catalogs", "DataCatalogsSummary"):
            results.append({
                "CatalogName": cat.get("CatalogName", " "),
                "Type": cat.get("Type", " "),
                "Status": cat.get("Status", " "),
            })
        if not results:
            results.append({"CatalogName": " ", "Type": " ", "Status": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("athena.list_data_catalogs(),region[%s],%s", ctx.region, err)
        results = [{"CatalogName": "ERROR CHECK", "Type": "ERROR CHECK", "Status": "ERROR CHECK"}]
    return results
