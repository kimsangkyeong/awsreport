####################################################################################################
#
# Purpose   : get Lambda functions (REGIONAL)
# Source    : lambda.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / lambda.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
# Note    : 'lambda' 는 파이썬 예약어이므로 import 는 importlib(collector) 로 로드된다.
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_functions(ctx) -> list[dict]:
    results = []
    try:
        lmb = ctx.get_client("lambda")
        for fn in paginate(lmb, "list_functions", "Functions"):
            vpc = fn.get("VpcConfig", {})
            subnets = vpc.get("SubnetIds", [])
            sgs = vpc.get("SecurityGroupIds", [])
            results.append({
                "FunctionName": fn.get("FunctionName", " "),
                "Runtime": fn.get("Runtime", " "),
                "Handler": fn.get("Handler", " "),
                "MemorySize": fn.get("MemorySize", " "),
                "Timeout": fn.get("Timeout", " "),
                "LastModified": fn.get("LastModified", " "),
                "VpcId": vpc.get("VpcId", " "),
                "VpcTName": "",
                "SubnetId": subnets[0] if subnets else " ",
                "SubnetTName": "",
                "Subnets": subnets if subnets else " ",
                "SecurityGroup": sgs if sgs else " ",
                "SecurityGroupTName": "",
                "KMSKeyArn": fn.get("KMSKeyArn", " "),
                "KeyAlias": "",
            })
        if not results:
            results.append({"FunctionName": " ", "Runtime": " ", "Handler": " ", "MemorySize": " ",
                            "Timeout": " ", "LastModified": " ", "VpcId": " ", "VpcTName": " ",
                            "SubnetId": " ", "SubnetTName": " ", "Subnets": " ", "SecurityGroup": " ",
                            "SecurityGroupTName": " ", "KMSKeyArn": " ", "KeyAlias": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("lambda.list_functions(),region[%s],%s", ctx.region, err)
        results = [{"FunctionName": "ERROR CHECK", "Runtime": "ERROR CHECK", "Handler": "ERROR CHECK",
                    "MemorySize": "ERROR CHECK", "Timeout": "ERROR CHECK", "LastModified": "ERROR CHECK",
                    "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                    "SubnetTName": "ERROR CHECK", "Subnets": "ERROR CHECK", "SecurityGroup": "ERROR CHECK",
                    "SecurityGroupTName": "ERROR CHECK", "KMSKeyArn": "ERROR CHECK", "KeyAlias": "ERROR CHECK"}]
    return results
