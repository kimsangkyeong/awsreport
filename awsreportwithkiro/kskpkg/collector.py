####################################################################################################
#
# Purpose   : registry-driven collection engine (sequential default / optional parallel)
# Source    : collector.py
# Usage     : from kskpkg.collector import Collector
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create
#
# Note    : depends_on 을 위상정렬하여 선행 리소스를 먼저 수집한다.
#           병렬(--parallel)은 depends_on 이 없는 동일 단계 서비스만 동시에 실행한다.
####################################################################################################
from __future__ import annotations

import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from . import enrich as enrich_mod
from . import discovery as discovery_mod
from .config import awsglobal
from .context import CollectContext, SessionFactory
from .registry import ServiceSpec


def _load_collector(dotted: str):
    """'kskpkg.module.func' 문자열에서 함수 로드 (lambda 등 예약어 모듈도 importlib 로 안전)."""
    idx = dotted.rfind(".")
    module_name, func_name = dotted[:idx], dotted[idx + 1:]
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def _results_to_dataframe(results) -> pd.DataFrame:
    """list[dict] (또는 list[list[dict]]) 을 DataFrame 으로 변환 (기존 설계 계승)."""
    df = pd.DataFrame()
    if not results:
        return df
    for result in results:
        df_tmp = pd.DataFrame(result if isinstance(result, list) else [result])
        df = pd.concat([df, df_tmp], ignore_index=True)
    return df


class Collector:
    def __init__(self, factory: SessionFactory, account_id: str, parallel: bool = False,
                 service_workers: int = 8, disabled: list | None = None):
        self.factory = factory
        self.account_id = account_id
        self.parallel = parallel
        self.service_workers = max(1, service_workers)
        self.disabled = set(disabled or [])

    # -- 단일 서비스 수집 --------------------------------------------------------
    def _collect_one(self, spec: ServiceSpec, ctx: CollectContext) -> pd.DataFrame:
        try:
            func = _load_collector(spec.collector)
            results = func(ctx)
            df = _results_to_dataframe(results)
            df = enrich_mod.apply_enrich(df, spec.enrich, ctx.deps)
            return df
        except Exception as err:  # noqa: BLE001
            awsglobal.klogger.error("collect %s (%s) 실패: %s", spec.key, spec.collector, err)
            return pd.DataFrame()

    # -- depends_on 위상정렬 -----------------------------------------------------
    @staticmethod
    def _topo_stages(specs: list[ServiceSpec]) -> list[list[ServiceSpec]]:
        """depends_on 기준 단계(stage) 분리. 같은 stage 는 서로 독립 → 병렬 가능."""
        key_set = {s.key for s in specs}
        resolved: set[str] = set()
        remaining = list(specs)
        stages: list[list[ServiceSpec]] = []
        while remaining:
            stage = [s for s in remaining
                     if all((d not in key_set) or (d in resolved) for d in s.depends_on)]
            if not stage:  # 순환/미해결 방지: 남은 것 한 번에 처리
                stage = remaining
            stages.append(sorted(stage, key=lambda s: s.order))
            for s in stage:
                resolved.add(s.key)
            remaining = [s for s in remaining if s.key not in resolved]
        return stages

    # -- 스코프 단위 수집 --------------------------------------------------------
    def run(self, specs: list[ServiceSpec], region: str,
            seed_deps: dict | None = None,
            discovered: "set[str] | None" = None) -> dict[str, pd.DataFrame]:
        """specs(단일 scope) 를 region 에서 수집. 반환: {key: DataFrame}.

        discovered 가 주어지면(조합 방식 C) should_collect 로 '존재하는 서비스만' 수집한다.
        None 이면 전량 수집(폴백/기존 동작).
        단, depends_on 으로 다른 서비스가 참조하는 선행 리소스는 생략돼도 enrich 가
        깨지지 않도록, '다른 수집 대상의 의존 대상'은 강제로 포함한다.
        """
        active = [s for s in specs if s.enabled and s.key not in self.disabled]

        if discovered is not None:
            # 1차: Discovery 기준 수집 대상
            selected = {s.key for s in active if discovery_mod.should_collect(s, discovered)}
            # 2차: 선택된 서비스의 depends_on 을 폐포(closure)로 추가 (enrich 선행 보장)
            spec_by_key = {s.key: s for s in active}
            changed = True
            while changed:
                changed = False
                for key in list(selected):
                    for dep in spec_by_key.get(key).depends_on if key in spec_by_key else []:
                        if dep in spec_by_key and dep not in selected:
                            selected.add(dep)
                            changed = True
            skipped = [s.key for s in active if s.key not in selected]
            if skipped:
                awsglobal.klogger.info("discovery 생략(미존재) region[%s]: %s", region, skipped)
            active = [s for s in active if s.key in selected]

        collected: dict[str, pd.DataFrame] = dict(seed_deps or {})
        results: dict[str, pd.DataFrame] = {}

        for stage in self._topo_stages(active):
            if self.parallel and len(stage) > 1:
                with ThreadPoolExecutor(max_workers=self.service_workers) as ex:
                    futures = {}
                    for spec in stage:
                        ctx = CollectContext(self.factory, region, self.account_id, dict(collected))
                        futures[ex.submit(self._collect_one, spec, ctx)] = spec
                    for fut in as_completed(futures):
                        spec = futures[fut]
                        df = fut.result()
                        collected[spec.key] = df
                        results[spec.key] = df
            else:
                for spec in stage:
                    ctx = CollectContext(self.factory, region, self.account_id, collected)
                    df = self._collect_one(spec, ctx)
                    collected[spec.key] = df
                    results[spec.key] = df

        return results
