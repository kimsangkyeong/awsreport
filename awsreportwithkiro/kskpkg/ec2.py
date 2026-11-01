####################################################################################################
#
# Purpose   : get EC2/VPC family resources
#             (vpc, subnet, igw, nat, eip, eni, instance, sg, prefixlist,
#              route table(router/routeinfo), vpc endpoint)
# Source    : ec2.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / ec2.py, ctx-based multi-region)
#  1.1      2026.11.01     add route tables(router/routeinfo), vpc endpoints
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import get_tag_name, paginate

klogger = awsglobal.klogger


def _err_row(columns: dict) -> list[dict]:
    return [columns]


def describe_vpcs(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for vpc in paginate(ec2, "describe_vpcs", "Vpcs"):
            results.append({
                "VpcId": vpc["VpcId"],
                "VpcTName": get_tag_name(vpc.get("Tags")),
                "CidrBlock": vpc.get("CidrBlock", " "),
                "State": vpc.get("State", " "),
                "IsDefault": vpc.get("IsDefault", " "),
                "Region": ctx.region,
            })
        if not results:
            results.append({"VpcId": " ", "VpcTName": " ", "CidrBlock": " ",
                            "State": " ", "IsDefault": " ", "Region": ctx.region})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_vpcs(),region[%s],%s", ctx.region, err)
        results = _err_row({"VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK",
                            "CidrBlock": "ERROR CHECK", "State": "ERROR CHECK",
                            "IsDefault": "ERROR CHECK", "Region": ctx.region})
    return results


def describe_subnets(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for sn in paginate(ec2, "describe_subnets", "Subnets"):
            results.append({
                "SubnetId": sn["SubnetId"],
                "SubnetTName": get_tag_name(sn.get("Tags")),
                "VpcId": sn.get("VpcId", " "),
                "VpcTName": "",
                "CidrBlock": sn.get("CidrBlock", " "),
                "AvailabilityZone": sn.get("AvailabilityZone", " "),
                "AvailableIpAddressCount": sn.get("AvailableIpAddressCount", " "),
                "MapPublicIpOnLaunch": sn.get("MapPublicIpOnLaunch", " "),
            })
        if not results:
            results.append({"SubnetId": " ", "SubnetTName": " ", "VpcId": " ", "VpcTName": " ",
                            "CidrBlock": " ", "AvailabilityZone": " ",
                            "AvailableIpAddressCount": " ", "MapPublicIpOnLaunch": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_subnets(),region[%s],%s", ctx.region, err)
        results = _err_row({"SubnetId": "ERROR CHECK", "SubnetTName": "ERROR CHECK",
                            "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK",
                            "CidrBlock": "ERROR CHECK", "AvailabilityZone": "ERROR CHECK",
                            "AvailableIpAddressCount": "ERROR CHECK", "MapPublicIpOnLaunch": "ERROR CHECK"})
    return results


def describe_internet_gateways(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for igw in paginate(ec2, "describe_internet_gateways", "InternetGateways"):
            attached = "Not Assigned"
            for att in igw.get("Attachments", []):
                if att.get("State") in ("available", "attached"):
                    attached = att.get("VpcId", "Not Assigned")
                    break
            results.append({
                "InternetGatewayId": igw["InternetGatewayId"],
                "InternetGatewayTName": get_tag_name(igw.get("Tags")),
                "AttachedVpcId": attached,
                "VpcTName": "",
            })
        if not results:
            results.append({"InternetGatewayId": " ", "InternetGatewayTName": " ",
                            "AttachedVpcId": " ", "VpcTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_internet_gateways(),region[%s],%s", ctx.region, err)
        results = _err_row({"InternetGatewayId": "ERROR CHECK", "InternetGatewayTName": "ERROR CHECK",
                            "AttachedVpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK"})
    return results


def describe_nat_gateways(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for nat in paginate(ec2, "describe_nat_gateways", "NatGateways"):
            addrs = nat.get("NatGatewayAddresses", [{}])
            first = addrs[0] if addrs else {}
            results.append({
                "NatGatewayId": nat["NatGatewayId"],
                "NatGatewayTName": get_tag_name(nat.get("Tags")),
                "VpcId": nat.get("VpcId", " "),
                "VpcTName": "",
                "SubnetId": nat.get("SubnetId", " "),
                "SubnetTName": "",
                "State": nat.get("State", " "),
                "AllocationId": first.get("AllocationId", " "),
                "EIPTName": "",
                "NetworkInterfaceId": first.get("NetworkInterfaceId", " "),
                "ENITName": "",
                "PublicIp": first.get("PublicIp", " "),
                "PrivateIp": first.get("PrivateIp", " "),
            })
        if not results:
            results.append({"NatGatewayId": " ", "NatGatewayTName": " ", "VpcId": " ", "VpcTName": " ",
                            "SubnetId": " ", "SubnetTName": " ", "State": " ", "AllocationId": " ",
                            "EIPTName": " ", "NetworkInterfaceId": " ", "ENITName": " ",
                            "PublicIp": " ", "PrivateIp": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_nat_gateways(),region[%s],%s", ctx.region, err)
        results = _err_row({"NatGatewayId": "ERROR CHECK", "NatGatewayTName": "ERROR CHECK",
                            "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                            "SubnetTName": "ERROR CHECK", "State": "ERROR CHECK", "AllocationId": "ERROR CHECK",
                            "EIPTName": "ERROR CHECK", "NetworkInterfaceId": "ERROR CHECK",
                            "ENITName": "ERROR CHECK", "PublicIp": "ERROR CHECK", "PrivateIp": "ERROR CHECK"})
    return results


def describe_addresses(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        resp = ec2.describe_addresses()
        for addr in resp.get("Addresses", []):
            results.append({
                "AllocationId": addr.get("AllocationId", " "),
                "EIPTName": get_tag_name(addr.get("Tags")),
                "PublicIp": addr.get("PublicIp", " "),
                "PrivateIpAddress": addr.get("PrivateIpAddress", " "),
                "Domain": addr.get("Domain", " "),
                "NetworkInterfaceId": addr.get("NetworkInterfaceId", " "),
                "ENITName": "",
                "InstanceId": addr.get("InstanceId", " "),
                "InstanceTName": "",
            })
        if not results:
            results.append({"AllocationId": " ", "EIPTName": " ", "PublicIp": " ",
                            "PrivateIpAddress": " ", "Domain": " ", "NetworkInterfaceId": " ",
                            "ENITName": " ", "InstanceId": " ", "InstanceTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_addresses(),region[%s],%s", ctx.region, err)
        results = _err_row({"AllocationId": "ERROR CHECK", "EIPTName": "ERROR CHECK", "PublicIp": "ERROR CHECK",
                            "PrivateIpAddress": "ERROR CHECK", "Domain": "ERROR CHECK",
                            "NetworkInterfaceId": "ERROR CHECK", "ENITName": "ERROR CHECK",
                            "InstanceId": "ERROR CHECK", "InstanceTName": "ERROR CHECK"})
    return results


def describe_network_interfaces(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for eni in paginate(ec2, "describe_network_interfaces", "NetworkInterfaces"):
            attach = eni.get("Attachment", {}) or {}
            results.append({
                "NetworkInterfaceId": eni["NetworkInterfaceId"],
                "ENITName": get_tag_name(eni.get("TagSet")),
                "VpcId": eni.get("VpcId", " "),
                "VpcTName": "",
                "SubnetId": eni.get("SubnetId", " "),
                "SubnetTName": "",
                "Status": eni.get("Status", " "),
                "PrivateIpAddress": eni.get("PrivateIpAddress", " "),
                "InterfaceType": eni.get("InterfaceType", " "),
                "Description": eni.get("Description", " "),
                "Attach_InstanceID": attach.get("InstanceId", " "),
                "Attach_InstanceTName": "",
            })
        if not results:
            results.append({"NetworkInterfaceId": " ", "ENITName": " ", "VpcId": " ", "VpcTName": " ",
                            "SubnetId": " ", "SubnetTName": " ", "Status": " ", "PrivateIpAddress": " ",
                            "InterfaceType": " ", "Description": " ", "Attach_InstanceID": " ",
                            "Attach_InstanceTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_network_interfaces(),region[%s],%s", ctx.region, err)
        results = _err_row({"NetworkInterfaceId": "ERROR CHECK", "ENITName": "ERROR CHECK",
                            "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                            "SubnetTName": "ERROR CHECK", "Status": "ERROR CHECK", "PrivateIpAddress": "ERROR CHECK",
                            "InterfaceType": "ERROR CHECK", "Description": "ERROR CHECK",
                            "Attach_InstanceID": "ERROR CHECK", "Attach_InstanceTName": "ERROR CHECK"})
    return results


def describe_instances(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for reservation in paginate(ec2, "describe_instances", "Reservations"):
            for inst in reservation.get("Instances", []):
                primary_eni = (inst.get("NetworkInterfaces") or [{}])[0]
                results.append({
                    "InstanceId": inst["InstanceId"],
                    "InstanceTName": get_tag_name(inst.get("Tags")),
                    "InstanceType": inst.get("InstanceType", " "),
                    "State": inst.get("State", {}).get("Name", " "),
                    "VpcId": inst.get("VpcId", " "),
                    "VpcTName": "",
                    "SubnetId": inst.get("SubnetId", " "),
                    "SubnetTName": "",
                    "PrivateIpAddress": inst.get("PrivateIpAddress", " "),
                    "PublicIpAddress": inst.get("PublicIpAddress", " "),
                    "NetworkInterfaceId": primary_eni.get("NetworkInterfaceId", " "),
                    "ENITName": "",
                    "ImageId": inst.get("ImageId", " "),
                    "LaunchTime": inst.get("LaunchTime").strftime("%Y-%m-%d %H:%M")
                    if inst.get("LaunchTime") else " ",
                })
        if not results:
            results.append({"InstanceId": " ", "InstanceTName": " ", "InstanceType": " ", "State": " ",
                            "VpcId": " ", "VpcTName": " ", "SubnetId": " ", "SubnetTName": " ",
                            "PrivateIpAddress": " ", "PublicIpAddress": " ", "NetworkInterfaceId": " ",
                            "ENITName": " ", "ImageId": " ", "LaunchTime": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_instances(),region[%s],%s", ctx.region, err)
        results = _err_row({"InstanceId": "ERROR CHECK", "InstanceTName": "ERROR CHECK",
                            "InstanceType": "ERROR CHECK", "State": "ERROR CHECK", "VpcId": "ERROR CHECK",
                            "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK", "SubnetTName": "ERROR CHECK",
                            "PrivateIpAddress": "ERROR CHECK", "PublicIpAddress": "ERROR CHECK",
                            "NetworkInterfaceId": "ERROR CHECK", "ENITName": "ERROR CHECK",
                            "ImageId": "ERROR CHECK", "LaunchTime": "ERROR CHECK"})
    return results


def describe_security_groups(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for sg in paginate(ec2, "describe_security_groups", "SecurityGroups"):
            results.append({
                "SGroupId": sg["GroupId"],
                "GroupId": sg["GroupId"],
                "SGroupName": sg.get("GroupName", " "),
                "SGroupTName": get_tag_name(sg.get("Tags")),
                "VpcId": sg.get("VpcId", " "),
                "VpcTName": "",
                "Description": sg.get("Description", " "),
                "IngressRuleCount": len(sg.get("IpPermissions", [])),
                "EgressRuleCount": len(sg.get("IpPermissionsEgress", [])),
            })
        if not results:
            results.append({"SGroupId": " ", "GroupId": " ", "SGroupName": " ", "SGroupTName": " ",
                            "VpcId": " ", "VpcTName": " ", "Description": " ",
                            "IngressRuleCount": " ", "EgressRuleCount": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_security_groups(),region[%s],%s", ctx.region, err)
        results = _err_row({"SGroupId": "ERROR CHECK", "GroupId": "ERROR CHECK", "SGroupName": "ERROR CHECK",
                            "SGroupTName": "ERROR CHECK", "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK",
                            "Description": "ERROR CHECK", "IngressRuleCount": "ERROR CHECK",
                            "EgressRuleCount": "ERROR CHECK"})
    return results


def describe_managed_prefix_lists(ctx) -> list[dict]:
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for pl in paginate(ec2, "describe_managed_prefix_lists", "PrefixLists"):
            results.append({
                "PrefixListId": pl.get("PrefixListId", " "),
                "PrefixListName": pl.get("PrefixListName", " "),
                "PrefixListTName": get_tag_name(pl.get("Tags")),
                "AddressFamily": pl.get("AddressFamily", " "),
                "MaxEntries": pl.get("MaxEntries", " "),
                "State": pl.get("State", " "),
                "OwnerId": pl.get("OwnerId", " "),
            })
        if not results:
            results.append({"PrefixListId": " ", "PrefixListName": " ", "PrefixListTName": " ",
                            "AddressFamily": " ", "MaxEntries": " ", "State": " ", "OwnerId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_managed_prefix_lists(),region[%s],%s", ctx.region, err)
        results = _err_row({"PrefixListId": "ERROR CHECK", "PrefixListName": "ERROR CHECK",
                            "PrefixListTName": "ERROR CHECK", "AddressFamily": "ERROR CHECK",
                            "MaxEntries": "ERROR CHECK", "State": "ERROR CHECK", "OwnerId": "ERROR CHECK"})
    return results


def describe_route_tables_assoc(ctx) -> list[dict]:
    """라우트 테이블 - 서브넷/게이트웨이 연결(association) 관점 sheet (router).

    연관 리소스 식별성을 위해 VpcTName / SubnetTName 자리를 둔다(enrich 로 채움).
    """
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for rt in paginate(ec2, "describe_route_tables", "RouteTables"):
            tagname = get_tag_name(rt.get("Tags"))
            assoc = rt.get("Associations", []) or []
            main_flag = "False"
            subnet_ids = []
            gateway_ids = []
            states = []
            assoc_ids = []
            for a in assoc:
                if a.get("Main") and a.get("AssociationState", {}).get("State") == "associated":
                    main_flag = "True"
                    if len(assoc) > 1:
                        continue
                assoc_ids.append(a.get("RouteTableAssociationId", " "))
                states.append(a.get("AssociationState", {}).get("State", " "))
                subnet_ids.append(a.get("SubnetId", "Not Setting"))
                gateway_ids.append(a.get("GatewayId", "Not Setting"))
            results.append({
                "RouteTableId": rt.get("RouteTableId", " "),
                "RouteTableTName": tagname,
                "Main": main_flag,
                "VpcId": rt.get("VpcId", " "),
                "VpcTName": "",
                "SubnetId": subnet_ids if subnet_ids else " ",
                "SubnetTName": "",
                "GatewayId": gateway_ids if gateway_ids else " ",
                "State": states if states else " ",
                "RouteTableAssociationId": assoc_ids if assoc_ids else " ",
            })
        if not results:
            results.append({"RouteTableId": " ", "RouteTableTName": " ", "Main": " ", "VpcId": " ",
                            "VpcTName": " ", "SubnetId": " ", "SubnetTName": " ", "GatewayId": " ",
                            "State": " ", "RouteTableAssociationId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_route_tables_assoc(),region[%s],%s", ctx.region, err)
        results = _err_row({"RouteTableId": "ERROR CHECK", "RouteTableTName": "ERROR CHECK", "Main": "ERROR CHECK",
                            "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                            "SubnetTName": "ERROR CHECK", "GatewayId": "ERROR CHECK", "State": "ERROR CHECK",
                            "RouteTableAssociationId": "ERROR CHECK"})
    return results


def describe_route_tables_routes(ctx) -> list[dict]:
    """라우트 테이블 - 라우트 항목(route) 관점 sheet (routeinfo).

    NAT/ENI 등 참조 리소스 식별성을 위해 NatGatewayTName / ENITName / VpcTName 자리를 둔다.
    """
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for rt in paginate(ec2, "describe_route_tables", "RouteTables"):
            tagname = get_tag_name(rt.get("Tags"))
            for route in rt.get("Routes", []):
                results.append({
                    "RouteTableId": rt.get("RouteTableId", " "),
                    "RouteTableTName": tagname,
                    "VpcId": rt.get("VpcId", " "),
                    "VpcTName": "",
                    "State": route.get("State", " "),
                    "Origin": route.get("Origin", " "),
                    "DestinationCidrBlock": route.get("DestinationCidrBlock", " "),
                    "DestinationPrefixListId": route.get("DestinationPrefixListId", " "),
                    "GatewayId": route.get("GatewayId", " "),
                    "NatGatewayId": route.get("NatGatewayId", " "),
                    "NatGatewayTName": "",
                    "InstanceId": route.get("InstanceId", " "),
                    "InstanceTName": "",
                    "NetworkInterfaceId": route.get("NetworkInterfaceId", " "),
                    "ENITName": "",
                    "TransitGatewayId": route.get("TransitGatewayId", " "),
                    "VpcPeeringConnectionId": route.get("VpcPeeringConnectionId", " "),
                })
        if not results:
            results.append({"RouteTableId": " ", "RouteTableTName": " ", "VpcId": " ", "VpcTName": " ",
                            "State": " ", "Origin": " ", "DestinationCidrBlock": " ",
                            "DestinationPrefixListId": " ", "GatewayId": " ", "NatGatewayId": " ",
                            "NatGatewayTName": " ", "InstanceId": " ", "InstanceTName": " ",
                            "NetworkInterfaceId": " ", "ENITName": " ", "TransitGatewayId": " ",
                            "VpcPeeringConnectionId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_route_tables_routes(),region[%s],%s", ctx.region, err)
        results = _err_row({"RouteTableId": "ERROR CHECK", "RouteTableTName": "ERROR CHECK", "VpcId": "ERROR CHECK",
                            "VpcTName": "ERROR CHECK", "State": "ERROR CHECK", "Origin": "ERROR CHECK",
                            "DestinationCidrBlock": "ERROR CHECK", "DestinationPrefixListId": "ERROR CHECK",
                            "GatewayId": "ERROR CHECK", "NatGatewayId": "ERROR CHECK", "NatGatewayTName": "ERROR CHECK",
                            "InstanceId": "ERROR CHECK", "InstanceTName": "ERROR CHECK",
                            "NetworkInterfaceId": "ERROR CHECK", "ENITName": "ERROR CHECK",
                            "TransitGatewayId": "ERROR CHECK", "VpcPeeringConnectionId": "ERROR CHECK"})
    return results


def describe_vpc_endpoints(ctx) -> list[dict]:
    """VPC Endpoint (Interface/Gateway/GatewayLoadBalancer).

    VpcTName / SubnetTName / SecurityGroupTName 자리로 연관 리소스 식별성 제공.
    """
    results = []
    try:
        ec2 = ctx.get_client("ec2")
        for ep in paginate(ec2, "describe_vpc_endpoints", "VpcEndpoints"):
            groups = [g.get("GroupId", " ") for g in ep.get("Groups", [])]
            subnets = ep.get("SubnetIds", []) or []
            results.append({
                "VpcEndpointId": ep.get("VpcEndpointId", " "),
                "VpcEndpointTName": get_tag_name(ep.get("Tags")),
                "VpcEndpointType": ep.get("VpcEndpointType", " "),
                "ServiceName": ep.get("ServiceName", " "),
                "State": ep.get("State", " "),
                "VpcId": ep.get("VpcId", " "),
                "VpcTName": "",
                "SubnetId": subnets[0] if subnets else " ",
                "SubnetTName": "",
                "SubnetIds": subnets if subnets else " ",
                "SecurityGroups": groups if groups else " ",
                "SecurityGroupTName": "",
                "PrivateDnsEnabled": ep.get("PrivateDnsEnabled", " "),
                "RouteTableIds": ep.get("RouteTableIds", " ") or " ",
            })
        if not results:
            results.append({"VpcEndpointId": " ", "VpcEndpointTName": " ", "VpcEndpointType": " ",
                            "ServiceName": " ", "State": " ", "VpcId": " ", "VpcTName": " ",
                            "SubnetId": " ", "SubnetTName": " ", "SubnetIds": " ", "SecurityGroups": " ",
                            "SecurityGroupTName": " ", "PrivateDnsEnabled": " ", "RouteTableIds": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ec2.describe_vpc_endpoints(),region[%s],%s", ctx.region, err)
        results = _err_row({"VpcEndpointId": "ERROR CHECK", "VpcEndpointTName": "ERROR CHECK",
                            "VpcEndpointType": "ERROR CHECK", "ServiceName": "ERROR CHECK", "State": "ERROR CHECK",
                            "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                            "SubnetTName": "ERROR CHECK", "SubnetIds": "ERROR CHECK", "SecurityGroups": "ERROR CHECK",
                            "SecurityGroupTName": "ERROR CHECK", "PrivateDnsEnabled": "ERROR CHECK",
                            "RouteTableIds": "ERROR CHECK"})
    return results
