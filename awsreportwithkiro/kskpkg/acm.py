####################################################################################################
#
# Purpose   : get ACM certificates (GLOBAL us-east-1 for CloudFront / REGIONAL per region)
# Source    : acm.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / acm.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/acm.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_certificates(ctx) -> list[dict]:
    results = []
    try:
        acm = ctx.get_client("acm")
        for cert in paginate(acm, "list_certificates", "CertificateSummaryList"):
            results.append({
                "CertificateArn": cert.get("CertificateArn", " "),
                "DomainName": cert.get("DomainName", " "),
                "Status": cert.get("Status", " "),
                "Type": cert.get("Type", " "),
                "KeyAlgorithm": cert.get("KeyAlgorithm", " "),
                "InUse": cert.get("InUse", " "),
                "Region": ctx.region,
            })
        if not results:
            results.append({"CertificateArn": " ", "DomainName": " ", "Status": " ",
                            "Type": " ", "KeyAlgorithm": " ", "InUse": " ", "Region": ctx.region})
    except Exception as err:  # noqa: BLE001
        klogger.error("acm.list_certificates(),region[%s],%s", ctx.region, err)
        results = [{"CertificateArn": "ERROR CHECK", "DomainName": "ERROR CHECK", "Status": "ERROR CHECK",
                    "Type": "ERROR CHECK", "KeyAlgorithm": "ERROR CHECK", "InUse": "ERROR CHECK",
                    "Region": ctx.region}]
    return results
