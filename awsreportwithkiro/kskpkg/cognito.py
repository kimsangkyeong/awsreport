####################################################################################################
#
# Purpose   : get Cognito identity pools and user pools (REGIONAL)
# Source    : cognito.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / cognito.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-identity.html
#           https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_identity_pools(ctx) -> list[dict]:
    results = []
    try:
        ci = ctx.get_client("cognito-identity")
        for pool in paginate(ci, "list_identity_pools", "IdentityPools", MaxResults=60):
            results.append({
                "IdentityPoolId": pool.get("IdentityPoolId", " "),
                "IdentityPoolName": pool.get("IdentityPoolName", " "),
            })
        if not results:
            results.append({"IdentityPoolId": " ", "IdentityPoolName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("cognito.list_identity_pools(),region[%s],%s", ctx.region, err)
        results = [{"IdentityPoolId": "ERROR CHECK", "IdentityPoolName": "ERROR CHECK"}]
    return results


def list_user_pools(ctx) -> list[dict]:
    results = []
    try:
        cidp = ctx.get_client("cognito-idp")
        for pool in paginate(cidp, "list_user_pools", "UserPools", MaxResults=60):
            results.append({
                "Id": pool.get("Id", " "),
                "Name": pool.get("Name", " "),
                "Status": pool.get("Status", " "),
                "CreationDate": pool.get("CreationDate").strftime("%Y-%m-%d %H:%M")
                if pool.get("CreationDate") else " ",
            })
        if not results:
            results.append({"Id": " ", "Name": " ", "Status": " ", "CreationDate": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("cognito.list_user_pools(),region[%s],%s", ctx.region, err)
        results = [{"Id": "ERROR CHECK", "Name": "ERROR CHECK", "Status": "ERROR CHECK", "CreationDate": "ERROR CHECK"}]
    return results
