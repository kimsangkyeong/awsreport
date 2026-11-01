####################################################################################################
#
# Purpose   : get EFS file systems (REGIONAL)
# Source    : efs.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / efs.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/efs.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import get_tag_name, paginate

klogger = awsglobal.klogger


def describe_file_systems(ctx) -> list[dict]:
    results = []
    try:
        efs = ctx.get_client("efs")
        for fs in paginate(efs, "describe_file_systems", "FileSystems"):
            results.append({
                "FileSystemId": fs.get("FileSystemId", " "),
                "FileSystemTName": get_tag_name(fs.get("Tags")) if fs.get("Tags") else fs.get("Name", " "),
                "LifeCycleState": fs.get("LifeCycleState", " "),
                "NumberOfMountTargets": fs.get("NumberOfMountTargets", " "),
                "SizeInBytes": fs.get("SizeInBytes", {}).get("Value", " "),
                "PerformanceMode": fs.get("PerformanceMode", " "),
                "ThroughputMode": fs.get("ThroughputMode", " "),
                "Encrypted": fs.get("Encrypted", " "),
                "KmsKeyId": fs.get("KmsKeyId", " "),
                "KmsKeyAlias": "",
            })
        if not results:
            results.append({"FileSystemId": " ", "FileSystemTName": " ", "LifeCycleState": " ",
                            "NumberOfMountTargets": " ", "SizeInBytes": " ", "PerformanceMode": " ",
                            "ThroughputMode": " ", "Encrypted": " ", "KmsKeyId": " ", "KmsKeyAlias": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("efs.describe_file_systems(),region[%s],%s", ctx.region, err)
        results = [{"FileSystemId": "ERROR CHECK", "FileSystemTName": "ERROR CHECK", "LifeCycleState": "ERROR CHECK",
                    "NumberOfMountTargets": "ERROR CHECK", "SizeInBytes": "ERROR CHECK",
                    "PerformanceMode": "ERROR CHECK", "ThroughputMode": "ERROR CHECK", "Encrypted": "ERROR CHECK",
                    "KmsKeyId": "ERROR CHECK", "KmsKeyAlias": "ERROR CHECK"}]
    return results
