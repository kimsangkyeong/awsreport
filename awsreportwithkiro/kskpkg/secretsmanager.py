####################################################################################################
#
# Purpose   : get Secrets Manager secrets (REGIONAL)
# Source    : secretsmanager.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / secretsmanager.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_secrets(ctx) -> list[dict]:
    results = []
    try:
        sm = ctx.get_client("secretsmanager")
        for s in paginate(sm, "list_secrets", "SecretList"):
            results.append({
                "Name": s.get("Name", " "),
                "ARN": s.get("ARN", " "),
                "Description": s.get("Description", " "),
                "KmsKeyId": s.get("KmsKeyId", " "),
                "KmsKeyAlias": "",
                "RotationEnabled": s.get("RotationEnabled", " "),
                "LastChangedDate": s.get("LastChangedDate").strftime("%Y-%m-%d %H:%M")
                if s.get("LastChangedDate") else " ",
            })
        if not results:
            results.append({"Name": " ", "ARN": " ", "Description": " ", "KmsKeyId": " ",
                            "KmsKeyAlias": " ", "RotationEnabled": " ", "LastChangedDate": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("secretsmanager.list_secrets(),region[%s],%s", ctx.region, err)
        results = [{"Name": "ERROR CHECK", "ARN": "ERROR CHECK", "Description": "ERROR CHECK",
                    "KmsKeyId": "ERROR CHECK", "KmsKeyAlias": "ERROR CHECK", "RotationEnabled": "ERROR CHECK",
                    "LastChangedDate": "ERROR CHECK"}]
    return results
