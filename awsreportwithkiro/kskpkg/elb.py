####################################################################################################
#
# Purpose   : get ELBv2 load balancers, listeners, listener rules,
#             target groups, target group bindings(target health) (REGIONAL)
# Source    : elb.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / elb.py, ctx-based)
#  1.1      2026.11.01     add listeners, listener rules, target groups, target health
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def describe_load_balancers(ctx) -> list[dict]:
    results = []
    try:
        elb = ctx.get_client("elbv2")
        for lb in paginate(elb, "describe_load_balancers", "LoadBalancers"):
            azs = [az.get("SubnetId", " ") for az in lb.get("AvailabilityZones", [])]
            # 다중 subnet 은 첫 subnet 을 대표로, 전체는 별도 컬럼
            first_subnet = azs[0] if azs else " "
            results.append({
                "LoadBalancerName": lb.get("LoadBalancerName", " "),
                "LoadBalancerArn": lb.get("LoadBalancerArn", " "),
                "Type": lb.get("Type", " "),
                "Scheme": lb.get("Scheme", " "),
                "State": lb.get("State", {}).get("Code", " "),
                "DNSName": lb.get("DNSName", " "),
                "VpcId": lb.get("VpcId", " "),
                "VpcTName": "",
                "SubnetId": first_subnet,
                "SubnetTName": "",
                "Subnets": azs if azs else " ",
                "SecurityGroups": lb.get("SecurityGroups", " ") or " ",
                "SecurityGroupTName": "",
            })
        if not results:
            results.append({"LoadBalancerName": " ", "LoadBalancerArn": " ", "Type": " ", "Scheme": " ",
                            "State": " ", "DNSName": " ", "VpcId": " ", "VpcTName": " ",
                            "SubnetId": " ", "SubnetTName": " ", "Subnets": " ", "SecurityGroups": " ",
                            "SecurityGroupTName": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("elb.describe_load_balancers(),region[%s],%s", ctx.region, err)
        results = [{"LoadBalancerName": "ERROR CHECK", "LoadBalancerArn": "ERROR CHECK", "Type": "ERROR CHECK",
                    "Scheme": "ERROR CHECK", "State": "ERROR CHECK", "DNSName": "ERROR CHECK",
                    "VpcId": "ERROR CHECK", "VpcTName": "ERROR CHECK", "SubnetId": "ERROR CHECK",
                    "SubnetTName": "ERROR CHECK", "Subnets": "ERROR CHECK", "SecurityGroups": "ERROR CHECK",
                    "SecurityGroupTName": "ERROR CHECK"}]
    return results


def _lb_arns_and_names(ctx):
    """deps['elb'] DataFrame 에서 (LoadBalancerArn 리스트, {arn: name} 매핑) 반환."""
    df = ctx.deps.get("elb")
    arns = []
    name_map = {}
    if df is not None and not df.empty and "LoadBalancerArn" in df.columns:
        for arn, name in zip(df["LoadBalancerArn"].tolist(),
                             df.get("LoadBalancerName", df["LoadBalancerArn"]).tolist()):
            if arn and arn not in (" ", "ERROR CHECK"):
                arns.append(arn)
                name_map[arn] = name
    return arns, name_map


def describe_listeners(ctx) -> list[dict]:
    """ELB 리스너. LoadBalancerName(=연관 ELB 식별) 포함."""
    results = []
    try:
        elb = ctx.get_client("elbv2")
        arns, name_map = _lb_arns_and_names(ctx)
        for lb_arn in arns:
            for lsn in paginate(elb, "describe_listeners", "Listeners", LoadBalancerArn=lb_arn):
                default_actions = lsn.get("DefaultActions", [])
                action_type = default_actions[0].get("Type", " ") if default_actions else " "
                target_arn = default_actions[0].get("TargetGroupArn", " ") if default_actions else " "
                certs = [c.get("CertificateArn", " ") for c in lsn.get("Certificates", [])]
                results.append({
                    "LoadBalancerArn": lb_arn,
                    "LoadBalancerName": name_map.get(lb_arn, " "),
                    "ListenerArn": lsn.get("ListenerArn", " "),
                    "Protocol": lsn.get("Protocol", " "),
                    "Port": lsn.get("Port", " "),
                    "SslPolicy": lsn.get("SslPolicy", " "),
                    "DefaultActionType": action_type,
                    "DefaultTargetGroupArn": target_arn,
                    "Certificates": certs if certs else " ",
                })
        if not results:
            results.append({"LoadBalancerArn": " ", "LoadBalancerName": " ", "ListenerArn": " ",
                            "Protocol": " ", "Port": " ", "SslPolicy": " ", "DefaultActionType": " ",
                            "DefaultTargetGroupArn": " ", "Certificates": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("elb.describe_listeners(),region[%s],%s", ctx.region, err)
        results = [{"LoadBalancerArn": "ERROR CHECK", "LoadBalancerName": "ERROR CHECK", "ListenerArn": "ERROR CHECK",
                    "Protocol": "ERROR CHECK", "Port": "ERROR CHECK", "SslPolicy": "ERROR CHECK",
                    "DefaultActionType": "ERROR CHECK", "DefaultTargetGroupArn": "ERROR CHECK",
                    "Certificates": "ERROR CHECK"}]
    return results


def describe_rules(ctx) -> list[dict]:
    """ELB 리스너 규칙. 소속 리스너/ELB 식별 정보 포함."""
    results = []
    try:
        elb = ctx.get_client("elbv2")
        arns, name_map = _lb_arns_and_names(ctx)
        # 리스너 ARN 수집 (LB 별)
        for lb_arn in arns:
            for lsn in paginate(elb, "describe_listeners", "Listeners", LoadBalancerArn=lb_arn):
                lsn_arn = lsn.get("ListenerArn", " ")
                try:
                    rules = elb.describe_rules(ListenerArn=lsn_arn).get("Rules", [])
                except Exception:  # noqa: BLE001
                    rules = []
                for rule in rules:
                    conditions = []
                    for cond in rule.get("Conditions", []):
                        field = cond.get("Field", " ")
                        vals = cond.get("Values", [])
                        conditions.append(f"{field}={vals}")
                    actions = [a.get("Type", " ") for a in rule.get("Actions", [])]
                    tgt_arns = []
                    for a in rule.get("Actions", []):
                        if a.get("TargetGroupArn"):
                            tgt_arns.append(a["TargetGroupArn"])
                    results.append({
                        "LoadBalancerName": name_map.get(lb_arn, " "),
                        "ListenerArn": lsn_arn,
                        "Protocol": lsn.get("Protocol", " "),
                        "Port": lsn.get("Port", " "),
                        "RuleArn": rule.get("RuleArn", " "),
                        "Priority": rule.get("Priority", " "),
                        "IsDefault": rule.get("IsDefault", " "),
                        "Conditions": conditions if conditions else " ",
                        "Actions": actions if actions else " ",
                        "TargetGroupArn": tgt_arns if tgt_arns else " ",
                    })
        if not results:
            results.append({"LoadBalancerName": " ", "ListenerArn": " ", "Protocol": " ", "Port": " ",
                            "RuleArn": " ", "Priority": " ", "IsDefault": " ", "Conditions": " ",
                            "Actions": " ", "TargetGroupArn": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("elb.describe_rules(),region[%s],%s", ctx.region, err)
        results = [{"LoadBalancerName": "ERROR CHECK", "ListenerArn": "ERROR CHECK", "Protocol": "ERROR CHECK",
                    "Port": "ERROR CHECK", "RuleArn": "ERROR CHECK", "Priority": "ERROR CHECK",
                    "IsDefault": "ERROR CHECK", "Conditions": "ERROR CHECK", "Actions": "ERROR CHECK",
                    "TargetGroupArn": "ERROR CHECK"}]
    return results


def describe_target_groups(ctx) -> list[dict]:
    """ELB 타깃 그룹. VpcTName / LoadBalancerName(연관 ELB) 식별 포함."""
    results = []
    try:
        elb = ctx.get_client("elbv2")
        _, name_map = _lb_arns_and_names(ctx)
        for tg in paginate(elb, "describe_target_groups", "TargetGroups"):
            lb_arns = tg.get("LoadBalancerArns", []) or []
            lb_names = [name_map.get(a, a) for a in lb_arns]
            results.append({
                "TargetGroupName": tg.get("TargetGroupName", " "),
                "TargetGroupArn": tg.get("TargetGroupArn", " "),
                "Protocol": tg.get("Protocol", " "),
                "Port": tg.get("Port", " "),
                "TargetType": tg.get("TargetType", " "),
                "VpcId": tg.get("VpcId", " "),
                "VpcTName": "",
                "LoadBalancerArns": lb_arns if lb_arns else " ",
                "LoadBalancerName": lb_names if lb_names else " ",
                "HealthCheckProtocol": tg.get("HealthCheckProtocol", " "),
                "HealthCheckPort": tg.get("HealthCheckPort", " "),
                "HealthCheckPath": tg.get("HealthCheckPath", " "),
            })
        if not results:
            results.append({"TargetGroupName": " ", "TargetGroupArn": " ", "Protocol": " ", "Port": " ",
                            "TargetType": " ", "VpcId": " ", "VpcTName": " ", "LoadBalancerArns": " ",
                            "LoadBalancerName": " ", "HealthCheckProtocol": " ", "HealthCheckPort": " ",
                            "HealthCheckPath": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("elb.describe_target_groups(),region[%s],%s", ctx.region, err)
        results = [{"TargetGroupName": "ERROR CHECK", "TargetGroupArn": "ERROR CHECK", "Protocol": "ERROR CHECK",
                    "Port": "ERROR CHECK", "TargetType": "ERROR CHECK", "VpcId": "ERROR CHECK",
                    "VpcTName": "ERROR CHECK", "LoadBalancerArns": "ERROR CHECK", "LoadBalancerName": "ERROR CHECK",
                    "HealthCheckProtocol": "ERROR CHECK", "HealthCheckPort": "ERROR CHECK",
                    "HealthCheckPath": "ERROR CHECK"}]
    return results


def describe_target_health(ctx) -> list[dict]:
    """타깃 그룹 바인딩(등록된 타깃과 상태). 타깃이 EC2 인스턴스면 InstanceTName 식별 제공."""
    results = []
    try:
        elb = ctx.get_client("elbv2")
        # 타깃 그룹 목록을 직접 조회 (deps 비의존, 대량 안전)
        tgs = list(paginate(elb, "describe_target_groups", "TargetGroups"))
        for tg in tgs:
            tg_arn = tg.get("TargetGroupArn", " ")
            tg_name = tg.get("TargetGroupName", " ")
            tg_type = tg.get("TargetType", " ")
            try:
                health = elb.describe_target_health(TargetGroupArn=tg_arn).get("TargetHealthDescriptions", [])
            except Exception:  # noqa: BLE001
                health = []
            if not health:
                results.append({
                    "TargetGroupName": tg_name, "TargetGroupArn": tg_arn, "TargetType": tg_type,
                    "TargetId": "No registered target", "TargetTName": " ", "Port": " ",
                    "AvailabilityZone": " ", "HealthState": " ", "HealthReason": " ",
                })
                continue
            for h in health:
                tgt = h.get("Target", {})
                hs = h.get("TargetHealth", {})
                target_id = tgt.get("Id", " ")
                results.append({
                    "TargetGroupName": tg_name,
                    "TargetGroupArn": tg_arn,
                    "TargetType": tg_type,
                    "TargetId": target_id,
                    # target 이 instance 타입이면 InstanceTName enrich 로 치환
                    "TargetTName": "" if tg_type == "instance" else " ",
                    "Port": tgt.get("Port", " "),
                    "AvailabilityZone": tgt.get("AvailabilityZone", " "),
                    "HealthState": hs.get("State", " "),
                    "HealthReason": hs.get("Reason", " "),
                })
        if not results:
            results.append({"TargetGroupName": " ", "TargetGroupArn": " ", "TargetType": " ",
                            "TargetId": " ", "TargetTName": " ", "Port": " ", "AvailabilityZone": " ",
                            "HealthState": " ", "HealthReason": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("elb.describe_target_health(),region[%s],%s", ctx.region, err)
        results = [{"TargetGroupName": "ERROR CHECK", "TargetGroupArn": "ERROR CHECK", "TargetType": "ERROR CHECK",
                    "TargetId": "ERROR CHECK", "TargetTName": "ERROR CHECK", "Port": "ERROR CHECK",
                    "AvailabilityZone": "ERROR CHECK", "HealthState": "ERROR CHECK", "HealthReason": "ERROR CHECK"}]
    return results
