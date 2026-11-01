####################################################################################################
#
# Purpose   : get Amazon SageMaker domains and endpoints (REGIONAL) - NEW AI service
# Source    : sagemaker.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (new AI service)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import log_optional_service, paginate

klogger = awsglobal.klogger


def list_domains(ctx) -> list[dict]:
    results = []
    try:
        sm = ctx.get_client("sagemaker")
        for d in paginate(sm, "list_domains", "Domains"):
            results.append({
                "DomainId": d.get("DomainId", " "),
                "DomainName": d.get("DomainName", " "),
                "Status": d.get("Status", " "),
                "Url": d.get("Url", " "),
                "CreationTime": d.get("CreationTime").strftime("%Y-%m-%d %H:%M")
                if d.get("CreationTime") else " ",
            })
        if not results:
            results.append({"DomainId": " ", "DomainName": " ", "Status": " ", "Url": " ", "CreationTime": " "})
    except Exception as err:  # noqa: BLE001
        log_optional_service(klogger, "sagemaker.list_domains()", ctx.region, err)
        results = [{"DomainId": " ", "DomainName": " ", "Status": " ", "Url": " ", "CreationTime": " "}]
    return results


def list_endpoints(ctx) -> list[dict]:
    results = []
    try:
        sm = ctx.get_client("sagemaker")
        for e in paginate(sm, "list_endpoints", "Endpoints"):
            results.append({
                "EndpointName": e.get("EndpointName", " "),
                "EndpointArn": e.get("EndpointArn", " "),
                "EndpointStatus": e.get("EndpointStatus", " "),
                "CreationTime": e.get("CreationTime").strftime("%Y-%m-%d %H:%M")
                if e.get("CreationTime") else " ",
                "LastModifiedTime": e.get("LastModifiedTime").strftime("%Y-%m-%d %H:%M")
                if e.get("LastModifiedTime") else " ",
            })
        if not results:
            results.append({"EndpointName": " ", "EndpointArn": " ", "EndpointStatus": " ",
                            "CreationTime": " ", "LastModifiedTime": " "})
    except Exception as err:  # noqa: BLE001
        log_optional_service(klogger, "sagemaker.list_endpoints()", ctx.region, err)
        results = [{"EndpointName": " ", "EndpointArn": " ", "EndpointStatus": " ",
                    "CreationTime": " ", "LastModifiedTime": " "}]
    return results
