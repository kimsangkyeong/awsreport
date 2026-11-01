####################################################################################################
#
# Purpose   : get S3 buckets (REGIONAL filtered by bucket location)
# Source    : s3.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / s3.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
# Note    : S3 는 글로벌 네임스페이스지만 버킷은 리전에 속한다. 현재 리전 버킷만 출력.
####################################################################################################
from __future__ import annotations

from .config import awsglobal

klogger = awsglobal.klogger


def list_buckets(ctx) -> list[dict]:
    results = []
    try:
        s3 = ctx.get_client("s3")
        buckets = s3.list_buckets().get("Buckets", [])
        for b in buckets:
            name = b["Name"]
            try:
                loc = s3.get_bucket_location(Bucket=name).get("LocationConstraint")
                region = loc or "us-east-1"
            except Exception:  # noqa: BLE001
                region = "unknown"
            if region != ctx.region:
                continue  # 현재 리전 버킷만

            kms_key = " "
            try:
                enc = s3.get_bucket_encryption(Bucket=name)
                rules = enc.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
                if rules:
                    sse = rules[0].get("ApplyServerSideEncryptionByDefault", {})
                    kms_key = sse.get("KMSMasterKeyID", sse.get("SSEAlgorithm", " "))
            except Exception:  # noqa: BLE001
                kms_key = " "

            results.append({
                "BucketName": name,
                "Region": region,
                "CreationDate": b.get("CreationDate").strftime("%Y-%m-%d %H:%M")
                if b.get("CreationDate") else " ",
                "KMSMasterKeyID": kms_key,
                "KMSMasterKeyAlias": "",
            })
        if not results:
            results.append({"BucketName": " ", "Region": ctx.region, "CreationDate": " ",
                            "KMSMasterKeyID": " ", "KMSMasterKeyAlias": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("s3.list_buckets(),region[%s],%s", ctx.region, err)
        results = [{"BucketName": "ERROR CHECK", "Region": ctx.region, "CreationDate": "ERROR CHECK",
                    "KMSMasterKeyID": "ERROR CHECK", "KMSMasterKeyAlias": "ERROR CHECK"}]
    return results
