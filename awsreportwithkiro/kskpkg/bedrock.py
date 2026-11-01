####################################################################################################
#
# Purpose   : get Amazon Bedrock custom models and guardrails (REGIONAL) - NEW AI service
# Source    : bedrock.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (new AI service)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock.html
# Note    : Bedrock 미지원 리전/구버전 boto3 는 빈 스켈레톤으로 안전 처리한다.
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import log_optional_service, paginate

klogger = awsglobal.klogger


def list_custom_models(ctx) -> list[dict]:
    results = []
    try:
        br = ctx.get_client("bedrock")
        for m in paginate(br, "list_custom_models", "modelSummaries"):
            results.append({
                "ModelName": m.get("modelName", " "),
                "ModelArn": m.get("modelArn", " "),
                "BaseModelName": m.get("baseModelName", " "),
                "CreationTime": m.get("creationTime").strftime("%Y-%m-%d %H:%M")
                if m.get("creationTime") else " ",
                "CustomizationType": m.get("customizationType", " "),
            })
        if not results:
            results.append({"ModelName": " ", "ModelArn": " ", "BaseModelName": " ",
                            "CreationTime": " ", "CustomizationType": " "})
    except Exception as err:  # noqa: BLE001
        log_optional_service(klogger, "bedrock.list_custom_models()", ctx.region, err)
        results = [{"ModelName": " ", "ModelArn": " ", "BaseModelName": " ",
                    "CreationTime": " ", "CustomizationType": " "}]
    return results


def list_guardrails(ctx) -> list[dict]:
    results = []
    try:
        br = ctx.get_client("bedrock")
        for g in paginate(br, "list_guardrails", "guardrails"):
            results.append({
                "Name": g.get("name", " "),
                "Id": g.get("id", " "),
                "Arn": g.get("arn", " "),
                "Status": g.get("status", " "),
                "Version": g.get("version", " "),
            })
        if not results:
            results.append({"Name": " ", "Id": " ", "Arn": " ", "Status": " ", "Version": " "})
    except Exception as err:  # noqa: BLE001
        log_optional_service(klogger, "bedrock.list_guardrails()", ctx.region, err)
        results = [{"Name": " ", "Id": " ", "Arn": " ", "Status": " ", "Version": " "}]
    return results
