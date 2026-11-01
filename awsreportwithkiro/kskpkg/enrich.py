####################################################################################################
#
# Purpose   : Tag Name cross-reference enrichment helpers (DataFrame based)
# Source    : enrich.py
# Usage     : from kskpkg import enrich
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py get_* helpers)
#
# Note    : 교차참조 치환은 "같은 리전 DataFrame 집합" 안에서만 수행한다.
#           (VPC/Subnet/SG 등은 리전 리소스이므로 타 리전 참조는 발생하지 않음)
####################################################################################################
from __future__ import annotations

import pandas as pd


def _build_lookup_map(df: "pd.DataFrame | None", id_col: str, name_col: str) -> dict:
    """선행 수집 DataFrame 에서 {id: name} 매핑을 1회 생성해 반환.

    매번 DataFrame 을 스캔하지 않고, 한 번 만든 dict 로 O(1) 치환하기 위한 캐시 소스.
    """
    if df is None or getattr(df, "empty", True):
        return {}
    if id_col not in df.columns or name_col not in df.columns:
        return {}
    mapping: dict = {}
    try:
        for key, name in zip(df[id_col].tolist(), df[name_col].tolist()):
            if key in (None, "", " "):
                continue
            # 동일 id 가 여러 행이면 의미있는 name 을 우선 보존
            if key not in mapping or mapping[key] in (None, "", " "):
                mapping[key] = name
    except Exception:  # noqa: BLE001
        return {}
    return mapping


def _resolve(mapping: dict, value, default: str = " "):
    """value(스칼라 또는 리스트)를 mapping 으로 치환.

    - 스칼라: mapping 에서 찾아 name 반환 (없으면 default)
    - 리스트/튜플: 각 원소를 치환한 리스트 반환 (리소스가 복수 참조하는 경우)
    """
    if isinstance(value, (list, tuple)):
        names = []
        for v in value:
            name = mapping.get(v)
            names.append(name if name not in (None, "", " ") else (v if v not in (None, "", " ") else default))
        return names if names else default
    name = mapping.get(value)
    if name not in (None, "", " "):
        return name
    return default


def _lookup(df, id_col: str, name_col: str, value, default: str = " "):
    """단건 조회 (하위 호환용). 내부적으로 매핑을 만들어 1건 치환."""
    return _resolve(_build_lookup_map(df, id_col, name_col), value, default)


# 기존 awsreport 의 get_* 함수군 (하위 호환). 단건 조회 시 매핑을 생성해 치환한다.
# 대량 치환은 apply_enrich 가 매핑을 1회만 만들어 사용하므로 효율적이다.

def get_vpcname(df, x):
    return _lookup(df, "VpcId", "VpcTName", x)


def get_subnetname(df, x):
    return _lookup(df, "SubnetId", "SubnetTName", x)


def get_sgname(df, x, tagname: bool = True):
    # securitygroup 모듈 컬럼: SGroupId(=GroupId) / SGroupName / SGroupTName
    name_col = "SGroupTName" if tagname else "SGroupName"
    return _lookup(df, "SGroupId", name_col, x)


def get_keyalias(df, x):
    return _lookup(df, "KeyArn", "KeyAlias", x)


def get_insname(df, x):
    return _lookup(df, "InstanceId", "InstanceTName", x)


def get_eniname(df, x):
    return _lookup(df, "NetworkInterfaceId", "ENITName", x)


def get_eipname(df, x):
    return _lookup(df, "AllocationId", "EIPTName", x)


def get_elbname(df, x):
    return _lookup(df, "LoadBalancerArn", "LoadBalancerName", x)


def get_ecsclustername(df, x):
    return _lookup(df, "ClusterArn", "ECSClusterName", x)


def get_natname(df, x):
    return _lookup(df, "NatGatewayId", "NatGatewayTName", x)


# enrich 규칙 디스패처 --------------------------------------------------------------
# registry 의 enrich 규칙 func_name 을 (id_col, name_col) 로 매핑.
# 선행 수집 DataFrame 에서 {id_col: name_col} 매핑을 1회 생성해 재사용한다.
_RESOLVER = {
    "get_vpcname": ("VpcId", "VpcTName"),
    "get_subnetname": ("SubnetId", "SubnetTName"),
    "get_sgname": ("SGroupId", "SGroupTName"),
    "get_keyalias": ("KeyArn", "KeyAlias"),
    "get_insname": ("InstanceId", "InstanceTName"),
    "get_eniname": ("NetworkInterfaceId", "ENITName"),
    "get_eipname": ("AllocationId", "EIPTName"),
    "get_elbname": ("LoadBalancerArn", "LoadBalancerName"),
    "get_ecsclustername": ("ClusterArn", "ECSClusterName"),
    "get_natname": ("NatGatewayId", "NatGatewayTName"),
}


def apply_enrich(df: "pd.DataFrame", rules: list, deps: dict) -> "pd.DataFrame":
    """registry 의 enrich 규칙을 DataFrame 에 적용.

    rule = (target_col, dep_key, func_name, source_col)
      - target_col : 생성/갱신할 컬럼 (예: VpcTName)
      - dep_key    : 참조할 선행 수집 DataFrame key (예: 'vpc')
      - func_name  : enrich 함수 이름 (_RESOLVER 키)
      - source_col : df 에서 id 를 읽을 컬럼 (예: VpcId). 스칼라/리스트 모두 지원.

    핵심: 선행 리소스 DataFrame 에서 {id: TagName} 매핑을 rule 당 1회만 생성(캐시)하고,
          대상 DataFrame 의 각 행은 이 매핑으로 O(1) 치환한다.
          (매 행마다 참조 DataFrame 전체를 재스캔하지 않음)
    """
    if df is None or df.empty or not rules:
        return df
    for rule in rules:
        try:
            target_col, dep_key, func_name, source_col = rule
        except ValueError:
            continue
        resolver = _RESOLVER.get(func_name)
        ref_df = deps.get(dep_key)
        if resolver is None or source_col not in df.columns:
            continue
        id_col, name_col = resolver
        mapping = _build_lookup_map(ref_df, id_col, name_col)  # 1회 생성
        df[target_col] = df[source_col].apply(lambda v: _resolve(mapping, v))
    return df
