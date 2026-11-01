####################################################################################################
#
# Purpose   : get SQS queues (REGIONAL)
# Source    : sqs.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / sqs.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_queues(ctx) -> list[dict]:
    results = []
    try:
        sqs = ctx.get_client("sqs")
        for url in paginate(sqs, "list_queues", "QueueUrls"):
            attrs = {}
            try:
                attrs = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["All"]).get("Attributes", {})
            except Exception:  # noqa: BLE001
                attrs = {}
            results.append({
                "QueueUrl": url,
                "QueueName": url.rsplit("/", 1)[-1],
                "ApproximateNumberOfMessages": attrs.get("ApproximateNumberOfMessages", " "),
                "FifoQueue": attrs.get("FifoQueue", "false"),
                "VisibilityTimeout": attrs.get("VisibilityTimeout", " "),
                "KmsMasterKeyId": attrs.get("KmsMasterKeyId", " "),
            })
        if not results:
            results.append({"QueueUrl": " ", "QueueName": " ", "ApproximateNumberOfMessages": " ",
                            "FifoQueue": " ", "VisibilityTimeout": " ", "KmsMasterKeyId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("sqs.list_queues(),region[%s],%s", ctx.region, err)
        results = [{"QueueUrl": "ERROR CHECK", "QueueName": "ERROR CHECK",
                    "ApproximateNumberOfMessages": "ERROR CHECK", "FifoQueue": "ERROR CHECK",
                    "VisibilityTimeout": "ERROR CHECK", "KmsMasterKeyId": "ERROR CHECK"}]
    return results
