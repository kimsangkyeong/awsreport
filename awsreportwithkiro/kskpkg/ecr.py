####################################################################################################
#
# Purpose   : get ECR repositories (REGIONAL)
# Source    : ecr.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / ecr.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_repositories(ctx) -> list[dict]:
    results = []
    try:
        ecr = ctx.get_client("ecr")
        for repo in paginate(ecr, "describe_repositories", "repositories"):
            enc = repo.get("encryptionConfiguration", {})
            results.append({
                "RepositoryName": repo.get("repositoryName", " "),
                "RepositoryUri": repo.get("repositoryUri", " "),
                "CreatedAt": repo.get("createdAt").strftime("%Y-%m-%d %H:%M")
                if repo.get("createdAt") else " ",
                "ImageTagMutability": repo.get("imageTagMutability", " "),
                "ScanOnPush": repo.get("imageScanningConfiguration", {}).get("scanOnPush", " "),
                "EncryptionType": enc.get("encryptionType", " "),
                "KmsKeyId": enc.get("kmsKey", " "),
                "KmsKeyAlias": "",
            })
        if not results:
            results.append({"RepositoryName": " ", "RepositoryUri": " ", "CreatedAt": " ",
                            "ImageTagMutability": " ", "ScanOnPush": " ", "EncryptionType": " ",
                            "KmsKeyId": " ", "KmsKeyAlias": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ecr.describe_repositories(),region[%s],%s", ctx.region, err)
        results = [{"RepositoryName": "ERROR CHECK", "RepositoryUri": "ERROR CHECK", "CreatedAt": "ERROR CHECK",
                    "ImageTagMutability": "ERROR CHECK", "ScanOnPush": "ERROR CHECK",
                    "EncryptionType": "ERROR CHECK", "KmsKeyId": "ERROR CHECK", "KmsKeyAlias": "ERROR CHECK"}]
    return results
