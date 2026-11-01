####################################################################################################
#
# Purpose   : collect context - boto3 session/client cache, SSO-safe credential pre-resolve
# Source    : context.py
# Usage     : from kskpkg.context import CollectContext
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
#           https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html
#
# Note    : botocore client 는 thread-safe 하지 않다. 병렬 수집 시 스레드/리전/서비스별로
#           독립 client 를 생성한다. AWS SSO 사용 시 다중 스레드가 동일 Session 의 토큰
#           갱신을 동시에 트리거하면 재인증 경합/연결 리셋이 발생할 수 있으므로,
#           병렬 시작 전에 credential 을 1회 선확정(freeze)하여 공유한다.
####################################################################################################
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.credentials import Credentials

from .config import awsglobal

# botocore 재시도 설정 (API throttling 흡수)
BOTO_CONFIG = Config(
    retries={"max_attempts": 10, "mode": "adaptive"},
    connect_timeout=10,
    read_timeout=60,
)


class SessionFactory:
    """profile/region 조합별 boto3 Session 및 client 를 생성/캐시한다.

    frozen_credentials 가 설정되면(=SSO 안전 병렬 모드) 모든 Session 을 정적
    credential 로 생성하여 스레드별 SSO refresh 를 방지한다.
    """

    def __init__(self, profile: str | None, frozen: Credentials | None = None):
        self._profile = profile
        self._frozen = frozen
        self._lock = threading.Lock()
        self._client_cache: dict[tuple[int, str, str], object] = {}

    def _build_session(self, region: str) -> boto3.Session:
        kwargs: dict = {"region_name": region}
        if self._frozen is not None:
            kwargs.update(
                aws_access_key_id=self._frozen.access_key,
                aws_secret_access_key=self._frozen.secret_key,
                aws_session_token=self._frozen.token,
            )
        elif self._profile:
            kwargs["profile_name"] = self._profile
        return boto3.Session(**kwargs)

    def client(self, service: str, region: str):
        """thread-id + service + region 단위 독립 client (thread-safe 보장)."""
        key = (threading.get_ident(), service, region)
        client = self._client_cache.get(key)
        if client is None:
            with self._lock:
                client = self._client_cache.get(key)
                if client is None:
                    session = self._build_session(region)
                    client = session.client(service, config=BOTO_CONFIG)
                    self._client_cache[key] = client
        return client


def resolve_account_id(profile: str | None, region: str) -> str:
    """sts:GetCallerIdentity 로 account id 조회."""
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
        else:
            session = boto3.Session(region_name=region)
        return session.client("sts", config=BOTO_CONFIG).get_caller_identity()["Account"]
    except Exception as err:  # noqa: BLE001
        awsglobal.klogger.error("resolve_account_id(),%s", err)
        return "unknown"


def freeze_credentials(profile: str | None, region: str):
    """SSO 안전 병렬을 위해 credential 을 1회 선확정.

    반환: (frozen_credentials | None, remaining_minutes | None)
    remaining_minutes 가 settings 임계값 미만이면 호출측에서 순차 폴백한다.
    """
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
        else:
            session = boto3.Session(region_name=region)
        creds = session.get_credentials()
        if creds is None:
            return None, None
        frozen = creds.get_frozen_credentials()

        remaining_minutes = None
        expiry = getattr(creds, "_expiry_time", None)
        if expiry is not None:
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            remaining_minutes = (expiry - datetime.now(timezone.utc)).total_seconds() / 60.0
        return frozen, remaining_minutes
    except Exception as err:  # noqa: BLE001
        awsglobal.klogger.error("freeze_credentials(),%s", err)
        return None, None


@dataclass
class CollectContext:
    """수집기(collector)에 전달되는 실행 컨텍스트.

    - get_client(service): 현재 리전/프로파일 적용 client (thread-safe)
    - region            : 현재 수집 리전
    - account_id        : 계정 id
    - deps              : 선행 수집 결과 DataFrame dict (key -> DataFrame)
    """

    factory: SessionFactory
    region: str
    account_id: str = "unknown"
    deps: dict = field(default_factory=dict)

    def get_client(self, service: str, region: str | None = None):
        return self.factory.client(service, region or self.region)
