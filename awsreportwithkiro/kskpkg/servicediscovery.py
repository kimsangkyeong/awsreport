####################################################################################################
#
# Purpose   : get Cloud Map (ServiceDiscovery) namespaces (REGIONAL)
# Source    : servicediscovery.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / servicediscovery.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/servicediscovery.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_namespaces(ctx) -> list[dict]:
    results = []
    try:
        sd = ctx.get_client("servicediscovery")
        for ns in paginate(sd, "list_namespaces", "Namespaces"):
            props = ns.get("Properties", {})
            results.append({
                "Name": ns.get("Name", " "),
                "Id": ns.get("Id", " "),
                "Type": ns.get("Type", " "),
                "ServiceCount": ns.get("ServiceCount", " "),
                "HostedZoneId": props.get("DnsProperties", {}).get("HostedZoneId", " "),
                "Description": ns.get("Description", " "),
            })
        if not results:
            results.append({"Name": " ", "Id": " ", "Type": " ", "ServiceCount": " ",
                            "HostedZoneId": " ", "Description": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("servicediscovery.list_namespaces(),region[%s],%s", ctx.region, err)
        results = [{"Name": "ERROR CHECK", "Id": "ERROR CHECK", "Type": "ERROR CHECK",
                    "ServiceCount": "ERROR CHECK", "HostedZoneId": "ERROR CHECK", "Description": "ERROR CHECK"}]
    return results
