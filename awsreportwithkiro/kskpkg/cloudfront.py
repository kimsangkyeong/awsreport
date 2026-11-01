####################################################################################################
#
# Purpose   : get CloudFront distributions / origin access identities (GLOBAL)
# Source    : cloudfront.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / cloudfront.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_distributions(ctx) -> list[dict]:
    results = []
    try:
        cf = ctx.get_client("cloudfront")
        paginator = cf.get_paginator("list_distributions")
        for page in paginator.paginate():
            dist_list = page.get("DistributionList", {}) or {}
            for dist in dist_list.get("Items", []) or []:
                origins = [o.get("DomainName", " ") for o in dist.get("Origins", {}).get("Items", [])]
                aliases = dist.get("Aliases", {}).get("Items", [])
                results.append({
                    "Id": dist.get("Id", " "),
                    "DomainName": dist.get("DomainName", " "),
                    "Aliases": aliases if aliases else " ",
                    "Status": dist.get("Status", " "),
                    "Enabled": dist.get("Enabled", " "),
                    "Origins": origins if origins else " ",
                    "PriceClass": dist.get("PriceClass", " "),
                    "WebACLId": dist.get("WebACLId", " "),
                    "Comment": dist.get("Comment", " "),
                })
        if not results:
            results.append({"Id": " ", "DomainName": " ", "Aliases": " ", "Status": " ",
                            "Enabled": " ", "Origins": " ", "PriceClass": " ", "WebACLId": " ", "Comment": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("cloudfront.list_distributions(),%s", err)
        results = [{"Id": "ERROR CHECK", "DomainName": "ERROR CHECK", "Aliases": "ERROR CHECK",
                    "Status": "ERROR CHECK", "Enabled": "ERROR CHECK", "Origins": "ERROR CHECK",
                    "PriceClass": "ERROR CHECK", "WebACLId": "ERROR CHECK", "Comment": "ERROR CHECK"}]
    return results


def list_cloud_front_origin_access_identities(ctx) -> list[dict]:
    results = []
    try:
        cf = ctx.get_client("cloudfront")
        paginator = cf.get_paginator("list_cloud_front_origin_access_identities")
        for page in paginator.paginate():
            oai_list = page.get("CloudFrontOriginAccessIdentityList", {}) or {}
            for oai in oai_list.get("Items", []) or []:
                results.append({
                    "Id": oai.get("Id", " "),
                    "S3CanonicalUserId": oai.get("S3CanonicalUserId", " "),
                    "Comment": oai.get("Comment", " "),
                })
        if not results:
            results.append({"Id": " ", "S3CanonicalUserId": " ", "Comment": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("cloudfront.list_cloud_front_origin_access_identities(),%s", err)
        results = [{"Id": "ERROR CHECK", "S3CanonicalUserId": "ERROR CHECK", "Comment": "ERROR CHECK"}]
    return results
