####################################################################################################
#
# Purpose   : get SNS topics with subscriptions (REGIONAL)
# Source    : sns.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / sns.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_topics_with_subscriptions(ctx) -> list[dict]:
    """topic 과 subscription 을 병합하여 반환 (기존 merge 로직 계승)."""
    results = []
    try:
        sns = ctx.get_client("sns")
        topics = [t.get("TopicArn", " ") for t in paginate(sns, "list_topics", "Topics")]
        subs_by_topic: dict[str, list] = {}
        for sub in paginate(sns, "list_subscriptions", "Subscriptions"):
            subs_by_topic.setdefault(sub.get("TopicArn", " "), []).append(sub)

        for topic_arn in topics:
            subs = subs_by_topic.get(topic_arn, [])
            if not subs:
                results.append({
                    "TopicArn": topic_arn, "Protocol": " ", "Endpoint": " ",
                    "SubscriptionArn": "No Subscriber", "Owner": " ",
                })
            else:
                for sub in subs:
                    results.append({
                        "TopicArn": topic_arn,
                        "Protocol": sub.get("Protocol", " "),
                        "Endpoint": sub.get("Endpoint", " "),
                        "SubscriptionArn": sub.get("SubscriptionArn", " "),
                        "Owner": sub.get("Owner", " "),
                    })
        if not results:
            results.append({"TopicArn": " ", "Protocol": " ", "Endpoint": " ",
                            "SubscriptionArn": " ", "Owner": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("sns.list_topics_with_subscriptions(),region[%s],%s", ctx.region, err)
        results = [{"TopicArn": "ERROR CHECK", "Protocol": "ERROR CHECK", "Endpoint": "ERROR CHECK",
                    "SubscriptionArn": "ERROR CHECK", "Owner": "ERROR CHECK"}]
    return results
