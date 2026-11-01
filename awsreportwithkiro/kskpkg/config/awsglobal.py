####################################################################################################
#
# Purpose   : define global variables, logger, settings loader for awsreportwithkiro
# Source    : awsglobal.py
# Usage     : import kskpkg.config.awsglobal
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / awsglobal.py)
#
####################################################################################################
from __future__ import annotations

import logging
import logging.config
import os

import yaml  # pip install pyyaml

# boto3 / botocore 로그 레벨 억제 (기존 설계 계승)
for _noisy in ("boto3", "botocore", "nose", "s3transfer", "urllib3"):
    logging.getLogger(_noisy).setLevel(logging.CRITICAL)

# 모듈 전역 (init_* 호출로 셋업)
klogger = logging.getLogger("logConsoleTypeA")
klogger_dat = logging.getLogger("datConsoleTypeC")

# 세션 관련 전역
profile_flag: bool = False
profile: str | None = None
region: str | None = None

# 설정 전역
settings: dict = {}


def init_logger(path: str) -> None:
    """logging.conf 경로를 받아 logger 초기화."""
    global klogger, klogger_dat
    logging.config.fileConfig(path, disable_existing_loggers=False)
    klogger = logging.getLogger("logConsoleTypeA")
    klogger_dat = logging.getLogger("datConsoleTypeC")


def init_settings(path: str) -> dict:
    """settings.yaml 로드. 파일이 없으면 기본값 반환."""
    global settings
    defaults = {
        "default_region": "ap-northeast-2",
        "regions": [],
        "global_region": "us-east-1",
        "output_prefix": "output",
        "concurrency": {"regions": 4, "services": 8},
        "sso_min_remaining_minutes": 15,
        "services": {"disabled": []},
    }
    loaded = {}
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
    # shallow merge (nested dict 는 defaults 를 base 로 update)
    merged = {**defaults, **loaded}
    merged["concurrency"] = {**defaults["concurrency"], **(loaded.get("concurrency") or {})}
    merged["services"] = {**defaults["services"], **(loaded.get("services") or {})}
    settings = merged
    return settings


def init_session(profile_name: str | None, region_name: str | None) -> bool:
    """AWS Session profile/region 전역 설정. (기존 로직 계승)"""
    global profile_flag, profile, region
    profile_flag = profile_name is not None
    profile = profile_name
    region = region_name
    if profile_flag and region is None:
        # profile 지정 시 region 은 settings/default 로 보완되므로 치명적이지 않음.
        # 하위 호환: 경고만 남기고 진행 허용.
        klogger.warning("profile 지정됨, region 미지정 → settings/default_region 사용")
    return True
