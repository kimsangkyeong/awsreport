####################################################################################################
#
# Purpose   : get API Gateway REST APIs (v1) and HTTP/WebSocket APIs (v2) (REGIONAL)
# Source    : apigateway.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (new service)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apigateway.html
#           https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apigatewayv2.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def get_rest_apis(ctx) -> list[dict]:
    results = []
    try:
        apig = ctx.get_client("apigateway")
        for api in paginate(apig, "get_rest_apis", "items"):
            results.append({
                "Id": api.get("id", " "),
                "Name": api.get("name", " "),
                "Description": api.get("description", " "),
                "EndpointType": ",".join(api.get("endpointConfiguration", {}).get("types", [])) or " ",
                "CreatedDate": api.get("createdDate").strftime("%Y-%m-%d %H:%M")
                if api.get("createdDate") else " ",
            })
        if not results:
            results.append({"Id": " ", "Name": " ", "Description": " ", "EndpointType": " ", "CreatedDate": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("apigateway.get_rest_apis(),region[%s],%s", ctx.region, err)
        results = [{"Id": "ERROR CHECK", "Name": "ERROR CHECK", "Description": "ERROR CHECK",
                    "EndpointType": "ERROR CHECK", "CreatedDate": "ERROR CHECK"}]
    return results


def get_apis_v2(ctx) -> list[dict]:
    results = []
    try:
        apig2 = ctx.get_client("apigatewayv2")
        token = None
        while True:
            kwargs = {"NextToken": token} if token else {}
            resp = apig2.get_apis(**kwargs)
            for api in resp.get("Items", []):
                results.append({
                    "ApiId": api.get("ApiId", " "),
                    "Name": api.get("Name", " "),
                    "ProtocolType": api.get("ProtocolType", " "),
                    "ApiEndpoint": api.get("ApiEndpoint", " "),
                    "CreatedDate": api.get("CreatedDate").strftime("%Y-%m-%d %H:%M")
                    if api.get("CreatedDate") else " ",
                })
            token = resp.get("NextToken")
            if not token:
                break
        if not results:
            results.append({"ApiId": " ", "Name": " ", "ProtocolType": " ",
                            "ApiEndpoint": " ", "CreatedDate": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("apigateway.get_apis_v2(),region[%s],%s", ctx.region, err)
        results = [{"ApiId": "ERROR CHECK", "Name": "ERROR CHECK", "ProtocolType": "ERROR CHECK",
                    "ApiEndpoint": "ERROR CHECK", "CreatedDate": "ERROR CHECK"}]
    return results
