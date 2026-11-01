####################################################################################################
#
# Purpose   : get MSK (Managed Streaming for Kafka) clusters (REGIONAL)
# Source    : kafka.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / kafka.py, ctx-based multi-region)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kafka.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import get_tag_name, paginate

klogger = awsglobal.klogger


def list_clusters(ctx) -> list[dict]:
    results = []
    try:
        kafka = ctx.get_client("kafka")
        for c in paginate(kafka, "list_clusters", "ClusterInfoList"):
            bng = c.get("BrokerNodeGroupInfo", {})
            subnets = bng.get("ClientSubnets", [])
            sgs = bng.get("SecurityGroups", [])
            enc = c.get("EncryptionInfo", {}).get("EncryptionAtRest", {})
            results.append({
                "ClusterName": c.get("ClusterName", " "),
                "ClusterTName": get_tag_name(c.get("Tags")),
                "State": c.get("State", " "),
                "CurrentVersion": c.get("CurrentVersion", " "),
                "NumberOfBrokerNodes": c.get("NumberOfBrokerNodes", " "),
                "InstanceType": bng.get("InstanceType", " "),
                "ClientSubnet": subnets[0] if subnets else " ",
                "ClientSubnetTName": "",
                "ClientSubnets": subnets if subnets else " ",
                "SecurityGroupId": sgs if sgs else " ",
                "SecurityGroupTName": "",
                "DataVolumeKMSKeyId": enc.get("DataVolumeKMSKeyId", " "),
                "DataVolumeKMSTName": "",
                "StorageMode": c.get("StorageMode", " "),
            })
        if not results:
            results.append({"ClusterName": " ", "ClusterTName": " ", "State": " ", "CurrentVersion": " ",
                            "NumberOfBrokerNodes": " ", "InstanceType": " ", "ClientSubnet": " ",
                            "ClientSubnetTName": " ", "ClientSubnets": " ", "SecurityGroupId": " ",
                            "SecurityGroupTName": " ", "DataVolumeKMSKeyId": " ", "DataVolumeKMSTName": " ",
                            "StorageMode": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("kafka.list_clusters(),region[%s],%s", ctx.region, err)
        results = [{"ClusterName": "ERROR CHECK", "ClusterTName": "ERROR CHECK", "State": "ERROR CHECK",
                    "CurrentVersion": "ERROR CHECK", "NumberOfBrokerNodes": "ERROR CHECK",
                    "InstanceType": "ERROR CHECK", "ClientSubnet": "ERROR CHECK", "ClientSubnetTName": "ERROR CHECK",
                    "ClientSubnets": "ERROR CHECK", "SecurityGroupId": "ERROR CHECK",
                    "SecurityGroupTName": "ERROR CHECK", "DataVolumeKMSKeyId": "ERROR CHECK",
                    "DataVolumeKMSTName": "ERROR CHECK", "StorageMode": "ERROR CHECK"}]
    return results
