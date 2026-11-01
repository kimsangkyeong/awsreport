####################################################################################################
#
# Purpose   : common utilities (list sync, paginator helper, tag extraction)
# Source    : utils.py
# Usage     : from kskpkg import utils
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / utils.py)
#
####################################################################################################
from __future__ import annotations

from botocore.exceptions import ClientError, EndpointConnectionError

from .config import awsglobal

# 서비스/오퍼레이션이 해당 리전에 없거나 활성화되지 않았음을 뜻하는 에러 코드.
# (코드 결함이 아니라 정상적인 "미지원" 상황 → 조용히 안내만)
_UNSUPPORTED_CODES = {
    "UnknownOperationException",   # 리전 엔드포인트가 해당 오퍼레이션 미제공
    "InvalidAction",               # 동일 취지
    "AccessDeniedException",       # 서비스 미활성/옵트인 전 (권한과 구분 어려워 안내 처리)
    "OptInRequired",
    "SubscriptionRequiredException",
    "ResourceNotFoundException",
}


def classify_aws_error(err) -> tuple[str, str]:
    """boto3 예외를 (분류, 간결 사유)로 변환.

    분류:
      'unsupported' : 미지원 리전/미활성 서비스 → INFO 수준 안내로 충분
      'endpoint'    : 해당 리전에 엔드포인트 없음 → INFO 수준
      'error'       : 그 외 실제 오류 → WARNING/ERROR 로 노출
    """
    if isinstance(err, EndpointConnectionError):
        return "endpoint", "해당 리전에 서비스 엔드포인트 없음"
    if isinstance(err, ClientError):
        code = err.response.get("Error", {}).get("Code", "")
        if code in _UNSUPPORTED_CODES:
            return "unsupported", f"리전 미지원/미활성({code})"
        return "error", code or str(err)
    return "error", str(err)


def log_optional_service(klogger, where: str, region: str, err) -> None:
    """옵셔널(신규 AI 등) 서비스 수집 실패를 분류에 맞춰 로깅.

    미지원/엔드포인트 없음은 INFO(조용히), 그 외는 WARNING(눈에 띄게).
    """
    kind, reason = classify_aws_error(err)
    if kind in ("unsupported", "endpoint"):
        klogger.info("%s region[%s] 수집 생략: %s", where, region, reason)
    else:
        klogger.warning("%s region[%s] 수집 오류: %s", where, region, reason)


def ListSyncCountWithSpace(*lists) -> bool:
    """입력 list 들의 길이를 최대 길이에 맞춰 공백으로 패딩 (기존 설계 계승).

    DataFrame 컬럼화를 위해 list-형 컬럼 간 길이를 맞춘다.
    """
    try:
        max_len = 1
        for lst in lists:
            max_len = max(max_len, len(lst))
        for lst in lists:
            for _ in range(len(lst), max_len):
                lst.append(" ")
        return True
    except Exception as err:  # noqa: BLE001
        awsglobal.klogger.error("utils.ListSyncCountWithSpace(),%s", err)
        return False


def get_tag_name(tags, key: str = "Name", default: str = "Not Exist Name Tag") -> str:
    """다양한 형태의 Tags 에서 Name 태그 값을 추출.

    지원 형태:
      - [{'Key': 'Name', 'Value': 'xxx'}, ...]   (EC2 스타일 list)
      - {'Name': 'xxx', ...}                      (dict 스타일, 예: MSK)
    """
    if not tags:
        return default
    if isinstance(tags, dict):
        return tags.get(key, default)
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, dict) and tag.get("Key") == key:
                return tag.get("Value", default)
    return default


def paginate(client, operation: str, result_key: str | None = None, **kwargs):
    """boto3 Paginator 가 있으면 페이지 순회, 없으면 단일 호출.

    result_key 가 주어지면 해당 키의 리스트를 평탄화해 yield,
    아니면 각 페이지(dict) 를 그대로 yield.
    대량 리소스를 자동 루프 처리하기 위한 공통 헬퍼.
    """
    if client.can_paginate(operation):
        paginator = client.get_paginator(operation)
        for page in paginator.paginate(**kwargs):
            if result_key is not None:
                for item in page.get(result_key, []) or []:
                    yield item
            else:
                yield page
    else:
        page = getattr(client, operation)(**kwargs)
        if result_key is not None:
            for item in page.get(result_key, []) or []:
                yield item
        else:
            yield page
