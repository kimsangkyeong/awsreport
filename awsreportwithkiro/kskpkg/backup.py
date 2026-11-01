####################################################################################################
#
# Purpose   : get AWS Backup plans and vaults (REGIONAL)
# Source    : backup.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / backup.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backup.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_backup_plans(ctx) -> list[dict]:
    results = []
    try:
        bk = ctx.get_client("backup")
        for p in paginate(bk, "list_backup_plans", "BackupPlansList"):
            results.append({
                "BackupPlanName": p.get("BackupPlanName", " "),
                "BackupPlanId": p.get("BackupPlanId", " "),
                "CreationDate": p.get("CreationDate").strftime("%Y-%m-%d %H:%M")
                if p.get("CreationDate") else " ",
                "LastExecutionDate": p.get("LastExecutionDate").strftime("%Y-%m-%d %H:%M")
                if p.get("LastExecutionDate") else " ",
                "VersionId": p.get("VersionId", " "),
            })
        if not results:
            results.append({"BackupPlanName": " ", "BackupPlanId": " ", "CreationDate": " ",
                            "LastExecutionDate": " ", "VersionId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("backup.list_backup_plans(),region[%s],%s", ctx.region, err)
        results = [{"BackupPlanName": "ERROR CHECK", "BackupPlanId": "ERROR CHECK", "CreationDate": "ERROR CHECK",
                    "LastExecutionDate": "ERROR CHECK", "VersionId": "ERROR CHECK"}]
    return results


def list_backup_vaults(ctx) -> list[dict]:
    results = []
    try:
        bk = ctx.get_client("backup")
        for v in paginate(bk, "list_backup_vaults", "BackupVaultList"):
            results.append({
                "BackupVaultName": v.get("BackupVaultName", " "),
                "NumberOfRecoveryPoints": v.get("NumberOfRecoveryPoints", " "),
                "EncryptionKeyArn": v.get("EncryptionKeyArn", " "),
                "KmsKeyAlias": "",
                "Locked": v.get("Locked", " "),
                "CreationDate": v.get("CreationDate").strftime("%Y-%m-%d %H:%M")
                if v.get("CreationDate") else " ",
            })
        if not results:
            results.append({"BackupVaultName": " ", "NumberOfRecoveryPoints": " ", "EncryptionKeyArn": " ",
                            "KmsKeyAlias": " ", "Locked": " ", "CreationDate": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("backup.list_backup_vaults(),region[%s],%s", ctx.region, err)
        results = [{"BackupVaultName": "ERROR CHECK", "NumberOfRecoveryPoints": "ERROR CHECK",
                    "EncryptionKeyArn": "ERROR CHECK", "KmsKeyAlias": "ERROR CHECK", "Locked": "ERROR CHECK",
                    "CreationDate": "ERROR CHECK"}]
    return results
