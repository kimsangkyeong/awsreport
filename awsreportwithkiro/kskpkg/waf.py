####################################################################################################
#
# Purpose   : get WAFv2 Web ACLs (CLOUDFRONT global scope / REGIONAL scope)
# Source    : waf.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / waf.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/wafv2.html
# Note    : CLOUDFRONT scope 는 반드시 us-east-1 엔드포인트로 호출해야 한다.
####################################################################################################
from __future__ import annotations

from .config import awsglobal

klogger = awsglobal.klogger


def _list_web_acls(ctx, scope: str, region: str) -> list[dict]:
    results = []
    try:
        wafv2 = ctx.get_client("wafv2", region)
        # list_web_acls 는 paginator 미지원 → NextMarker 수동 루프 (Limit 최대 100)
        acls = []
        marker = None
        while True:
            kwargs = {"Scope": scope, "Limit": 100}
            if marker:
                kwargs["NextMarker"] = marker
            resp = wafv2.list_web_acls(**kwargs)
            acls.extend(resp.get("WebACLs", []))
            marker = resp.get("NextMarker")
            if not marker or not resp.get("WebACLs"):
                break
        for acl in acls:
            results.append({
                "Name": acl.get("Name", " "),
                "Id": acl.get("Id", " "),
                "Scope": scope,
                "ARN": acl.get("ARN", " "),
                "Description": acl.get("Description", " "),
                "LockToken": acl.get("LockToken", " "),
            })
        if not results:
            results.append({"Name": " ", "Id": " ", "Scope": scope, "ARN": " ",
                            "Description": " ", "LockToken": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("waf.list_web_acls(scope=%s),%s", scope, err)
        results = [{"Name": "ERROR CHECK", "Id": "ERROR CHECK", "Scope": scope, "ARN": "ERROR CHECK",
                    "Description": "ERROR CHECK", "LockToken": "ERROR CHECK"}]
    return results


def list_web_acls_cloudfront(ctx) -> list[dict]:
    # CLOUDFRONT scope 는 us-east-1 고정
    return _list_web_acls(ctx, "CLOUDFRONT", "us-east-1")


def list_web_acls_regional(ctx) -> list[dict]:
    return _list_web_acls(ctx, "REGIONAL", ctx.region)
