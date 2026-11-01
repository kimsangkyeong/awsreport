####################################################################################################
#
# Purpose   : get Amazon Bedrock AgentCore Gateways and targets (REGIONAL) - NEW AI service
# Source    : bedrock_agentcore.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (new AI service)
#
# Ref     : https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-agentcore-control/client/list_gateways.html
#           https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-agentcore-control/client/list_gateway_targets.html
# Note    : client 명은 'bedrock-agentcore-control'. 미지원 리전/구버전 boto3 는 빈 스켈레톤 처리.
#           gateway 요약과 gateway 별 target 요약을 1개 sheet 로 평탄화하여 함께 제공한다.
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import log_optional_service

klogger = awsglobal.klogger

_COLUMNS = {
    "GatewayId": " ", "GatewayName": " ", "Status": " ", "AuthorizerType": " ",
    "ProtocolType": " ", "Description": " ", "CreatedAt": " ", "UpdatedAt": " ",
    "TargetId": " ", "TargetName": " ", "TargetStatus": " ",
}


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else " "


def _list_gateways(client):
    if client.can_paginate("list_gateways"):
        for page in client.get_paginator("list_gateways").paginate():
            yield from page.get("items", [])
    else:
        token = None
        while True:
            kwargs = {"nextToken": token} if token else {}
            resp = client.list_gateways(**kwargs)
            yield from resp.get("items", [])
            token = resp.get("nextToken")
            if not token:
                break


def _list_targets(client, gateway_id):
    try:
        if client.can_paginate("list_gateway_targets"):
            for page in client.get_paginator("list_gateway_targets").paginate(gatewayIdentifier=gateway_id):
                yield from page.get("items", [])
        else:
            resp = client.list_gateway_targets(gatewayIdentifier=gateway_id)
            yield from resp.get("items", [])
    except Exception as err:  # noqa: BLE001
        log_optional_service(klogger, f"bedrock_agentcore.list_gateway_targets({gateway_id})", "", err)


def list_gateways(ctx) -> list[dict]:
    results = []
    try:
        client = ctx.get_client("bedrock-agentcore-control")
        for gw in _list_gateways(client):
            gw_id = gw.get("gatewayId", " ")
            base = {
                "GatewayId": gw_id,
                "GatewayName": gw.get("name", " "),
                "Status": gw.get("status", " "),
                "AuthorizerType": gw.get("authorizerType", " "),
                "ProtocolType": gw.get("protocolType", " "),
                "Description": gw.get("description", " "),
                "CreatedAt": _fmt(gw.get("createdAt")),
                "UpdatedAt": _fmt(gw.get("updatedAt")),
            }
            targets = list(_list_targets(client, gw_id))
            if not targets:
                results.append({**_COLUMNS, **base})
            else:
                for t in targets:
                    results.append({**_COLUMNS, **base,
                                    "TargetId": t.get("targetId", " "),
                                    "TargetName": t.get("name", " "),
                                    "TargetStatus": t.get("status", " ")})
        if not results:
            results.append(dict(_COLUMNS))
    except Exception as err:  # noqa: BLE001
        log_optional_service(klogger, "bedrock_agentcore.list_gateways()", ctx.region, err)
        results = [dict(_COLUMNS)]
    return results
