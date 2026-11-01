####################################################################################################
#
# Purpose   : get KMS keys with alias (REGIONAL)
# Source    : kms.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / kms.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_keys(ctx) -> list[dict]:
    results = []
    try:
        kms = ctx.get_client("kms")
        # alias 매핑 (KeyId -> AliasName)
        alias_map: dict[str, str] = {}
        for alias in paginate(kms, "list_aliases", "Aliases"):
            if "TargetKeyId" in alias:
                alias_map[alias["TargetKeyId"]] = alias.get("AliasName", " ")

        for key in paginate(kms, "list_keys", "Keys"):
            key_id = key.get("KeyId", " ")
            key_arn = key.get("KeyArn", " ")
            try:
                meta = kms.describe_key(KeyId=key_id).get("KeyMetadata", {})
            except Exception:  # noqa: BLE001
                meta = {}
            results.append({
                "KeyArn": key_arn,
                "KeyId": key_id,
                "KeyAlias": alias_map.get(key_id, " "),
                "KeyManager": meta.get("KeyManager", " "),
                "KeyState": meta.get("KeyState", " "),
                "KeyUsage": meta.get("KeyUsage", " "),
                "Description": meta.get("Description", " "),
            })
        if not results:
            results.append({"KeyArn": " ", "KeyId": " ", "KeyAlias": " ", "KeyManager": " ",
                            "KeyState": " ", "KeyUsage": " ", "Description": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("kms.list_keys(),region[%s],%s", ctx.region, err)
        results = [{"KeyArn": "ERROR CHECK", "KeyId": "ERROR CHECK", "KeyAlias": "ERROR CHECK",
                    "KeyManager": "ERROR CHECK", "KeyState": "ERROR CHECK", "KeyUsage": "ERROR CHECK",
                    "Description": "ERROR CHECK"}]
    return results
