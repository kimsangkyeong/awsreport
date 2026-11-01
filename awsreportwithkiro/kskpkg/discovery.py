####################################################################################################
#
# Purpose   : account resource discovery via Resource Groups Tagging API
# Source    : discovery.py
# Usage     : from kskpkg.discovery import discover_services
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (조합 방식 C: 존재 서비스만 상세 수집)
#
# Ref     : https://docs.aws.amazon.com/resourcegroupstagging/latest/APIReference/API_GetResources.html
#
# 동작 : resourcegroupstaggingapi:GetResources 로 리전 내 리소스 ARN 을 끝까지 조회하고,
#        ARN 의 service 토큰 집합(예: 'ec2','elasticloadbalancing','rds' ...)을 반환한다.
#        이 집합을 레지스트리의 arn_services 와 대조해 "존재하는 서비스만" 상세 수집한다.
#
# 주의 : Tagging API 는 태그/추적 기반이라 커버리지 밖 리소스가 있을 수 있다.
#        따라서 Discovery 는 '포함 여부 힌트'로만 쓰고, always_collect 서비스와
#        Discovery 실패 시에는 전량 수집으로 폴백하여 누락을 방지한다.
####################################################################################################
from __future__ import annotations

from .config import awsglobal

klogger = awsglobal.klogger


def _service_token_from_arn(arn: str) -> str | None:
    """ARN 에서 service 토큰 추출.

    arn:partition:service:region:account-id:resource...
    예) arn:aws:ec2:ap-northeast-2:123:instance/i-abc -> 'ec2'
        arn:aws:elasticloadbalancing:...:loadbalancer/app/... -> 'elasticloadbalancing'
    """
    parts = arn.split(":")
    if len(parts) >= 3 and parts[0] == "arn":
        return parts[2] or None
    return None


def discover_services(ctx) -> set[str] | None:
    """현재 ctx.region 에 존재하는 서비스 토큰 집합을 반환.

    반환:
      set[str] : 발견된 service 토큰 집합 (비어 있어도 set)
      None     : Discovery 실패 (호출측에서 전량 수집으로 폴백)
    """
    try:
        client = ctx.get_client("resourcegroupstaggingapi")
        services: set[str] = set()
        paginator = client.get_paginator("get_resources")
        for page in paginator.paginate(ResourcesPerPage=100):
            for item in page.get("ResourceTagMappingList", []):
                arn = item.get("ResourceARN", "")
                token = _service_token_from_arn(arn)
                if token:
                    services.add(token)
        klogger.info("discovery region[%s]: %d개 서비스 발견 %s",
                     ctx.region, len(services), sorted(services))
        return services
    except Exception as err:  # noqa: BLE001
        klogger.warning("discovery region[%s] 실패 → 전량 수집 폴백: %s", ctx.region, err)
        return None


def should_collect(spec, discovered: set[str] | None) -> bool:
    """Discovery 결과 기준으로 해당 서비스 수집 여부 판정.

    - discovered is None (Discovery 미수행/실패) : True (전량 폴백)
    - always_collect                            : True (선행 의존/커버리지 밖 안전)
    - arn_services 가 비어 있음                 : True (판정 근거 없음 → 보수적으로 포함)
    - arn_services 와 discovered 교집합 존재     : True
    - 그 외                                     : False (생략)
    """
    if discovered is None:
        return True
    if getattr(spec, "always_collect", False):
        return True
    arn_services = getattr(spec, "arn_services", []) or []
    if not arn_services:
        return True
    return any(s in discovered for s in arn_services)
