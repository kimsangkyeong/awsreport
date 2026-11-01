####################################################################################################
#
# Purpose   : aws operator main program (multi-region, registry-driven, AI services)
# Source    : awsreportwithkiro.py
# Usage     : python awsreportwithkiro.py [--profile NAME] [--region R1 R2 ...] [--parallel] [-o NAME]
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py)
#
# ref     : https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html
#           https://xlsxwriter.readthedocs.io/index.html
#           https://boto3.amazonaws.com/v1/documentation/api/latest/
# required install package : pip install -r requirements.txt
#
####################################################################################################
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

import pandas as pd  # pip install pandas

import kskpkg.config.awsglobal as awsglobal
from kskpkg import excel
from kskpkg.collector import Collector
from kskpkg.context import CollectContext, SessionFactory, freeze_credentials, resolve_account_id
from kskpkg.discovery import discover_services
from kskpkg.registry import SERVICE_REGISTRY
from kskpkg import diffreport

pd.set_option("display.max_colwidth", 999)
pd.set_option("display.max_rows", 150)


def cmd_parse():
    parser = argparse.ArgumentParser(
        description="AWS service information automatic extraction and report generation program (with kiro)."
    )
    parser.add_argument("--profile", dest="profile_name", default=None, help="AWS Session Profile Name")
    parser.add_argument("--region", dest="region_names", nargs="*", default=None,
                        help="대상 리전 목록 (공백 구분). 미지정 시 settings.yaml 사용")
    parser.add_argument("--parallel", dest="parallel", action="store_true",
                        help="서비스 병렬 수집 (SSO credential 선확정 안전장치 적용)")
    parser.add_argument("--full", dest="full", action="store_true",
                        help="Discovery 를 끄고 모든 서비스를 전량 수집 (없는 서비스도 호출/빈 sheet 생성)")
    parser.add_argument("--no-discover", dest="no_discover", action="store_true",
                        help="--full 과 동일 (Discovery 비활성, 전량 수집)")
    parser.add_argument("--no-diff", dest="no_diff", action="store_true",
                        help="이전 리포트와의 변경 비교(diff) 생성을 끈다")
    parser.add_argument("--init-config", dest="init_config", action="store_true",
                        help="실행 파일 옆에 편집 가능한 settings.yaml 을 생성하고 종료 (단일 실행파일 배포용)")
    parser.add_argument("-o", dest="output_filename", default=None, help="출력 파일 접두어")
    return parser.parse_args()


def init_config():
    """번들된 기본 settings.yaml 을 실행 파일 옆에 복사한다.

    단일 실행파일(.exe) 사용자는 소스를 편집할 수 없으므로, 이 명령으로 생성된
    settings.yaml 을 수정하면 _paths() 가 이를 우선 로드한다.
    """
    _, _, _ = _paths()  # logger 미초기화 상태라 print 사용
    base = _resource_base()
    src = os.path.join(base, "kskpkg", "config", "settings.yaml")
    dst = os.path.join(_exe_dir(), "settings.yaml")
    if os.path.exists(dst):
        print(f"이미 존재합니다(덮어쓰지 않음): {dst}")
        return
    try:
        import shutil
        shutil.copyfile(src, dst)
        print(f"생성됨: {dst}")
        print("이 파일의 regions/global_region/discovery/diff 등을 수정한 뒤 다시 실행하세요.")
    except Exception as err:  # noqa: BLE001
        print(f"settings.yaml 생성 실패: {err}")


def _resource_base():
    """리소스(설정/로그 conf) 기준 디렉토리.

    - PyInstaller onefile 로 패키징되면 번들이 sys._MEIPASS 에 풀린다.
    - 일반 실행이면 이 소스 파일 기준.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def _exe_dir():
    """실행 파일(또는 스크립트)이 위치한 디렉토리. 사용자 편집 settings 탐색용."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _paths():
    path_cwd = os.getcwd()
    base = _resource_base()
    path_logconf = os.path.join(base, "kskpkg", "config", "logging.conf")
    bundled_settings = os.path.join(base, "kskpkg", "config", "settings.yaml")
    # settings.yaml 은 사용자가 수정할 수 있어야 하므로, 실행 파일 옆 > CWD > 번들 순으로 탐색.
    candidates = [
        os.path.join(_exe_dir(), "settings.yaml"),
        os.path.join(path_cwd, "settings.yaml"),
        bundled_settings,
    ]
    path_settings = next((p for p in candidates if os.path.exists(p)), bundled_settings)
    return path_cwd, path_logconf, path_settings


def global_config_init(args):
    _, path_logconf, path_settings = _paths()
    awsglobal.init_logger(path_logconf)
    settings = awsglobal.init_settings(path_settings)
    awsglobal.init_session(args.profile_name, (args.region_names or [None])[0])
    return settings


def resolve_regions(args, settings) -> list[str]:
    """수집 대상 리전 목록(원본)을 반환. global_region 포함 여부는 여기서 거르지 않는다."""
    if args.region_names:
        return args.region_names
    if settings.get("regions"):
        return settings["regions"]
    return [settings["default_region"]]


def resolve_output_regions(regions: list[str], global_region: str) -> list[str]:
    """실제 Excel 파일을 생성할 리전 목록.

    global_region(예: us-east-1)은 글로벌 리소스 전용 수집 리전일 뿐,
    단독으로 출력 파일을 만들지 않는다. regions 에서 global_region 을 제외하고,
    순서를 보존하며 중복을 제거한다.

    예) global=us-east-1
        regions=[us-east-1, ap-northeast-2]              -> [ap-northeast-2]            (파일 1개)
        regions=[us-east-1, ap-northeast-2, ap-northeast-1] -> [ap-northeast-2, ap-northeast-1] (파일 2개)
    글로벌 리소스는 생성되는 각 리전 파일에 공통으로 중복 포함된다.

    단, 출력 대상이 하나도 남지 않으면(regions 가 global_region 뿐이면)
    global_region 자체를 출력 리전으로 사용한다(글로벌 리소스를 담을 파일 확보).
    """
    seen = set()
    output = []
    for r in regions:
        if r == global_region:
            continue
        if r in seen:
            continue
        seen.add(r)
        output.append(r)
    if not output:
        output = [global_region]
    return output


def build_output_path(prefix: str, account_id: str, region: str, cwd: str) -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    return os.path.join(cwd, f"{prefix}_{account_id}_{region}_{ts}.xlsx")


def _is_empty_df(df) -> bool:
    """수집 결과가 '실데이터 없음'인지 판정.

    모듈은 비어 있을 때 컬럼 스켈레톤(모든 값이 공백/placeholder)을 1행 반환하므로,
    '행이 없거나' '모든 셀이 공백/placeholder' 이면 빈 것으로 본다.
    """
    if df is None or df.empty:
        return True
    placeholders = {"", " ", "No Subscriber", "  No Subscriber  ",
                    "No registered target", "Not Setting", "Not Assigned"}

    def _blank(v):
        if isinstance(v, (list, tuple)):
            return all(str(x).strip() in placeholders or str(x).strip() == "" for x in v) or len(v) == 0
        return str(v).strip() in placeholders or str(v).strip() == ""

    for _, row in df.iterrows():
        if not all(_blank(v) for v in row.values):
            return False
    return True


def write_excel(path: str, global_results: dict, region_results: dict, ordered_specs,
                emit_empty: bool = True) -> int:
    """글로벌 공통 sheet + 리전 sheet 를 order 순서로 기록.

    emit_empty=False 면 '실데이터 없는' sheet 는 생성하지 않는다(조합 방식 기본).
    반환: 기록한 sheet 수.
    """
    klogger_dat = awsglobal.klogger_dat
    klogger_dat.info("%s save to excel: %s", "-" * 20, path)
    written = 0
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        for spec in ordered_specs:
            df = global_results.get(spec.key) if spec.scope == "GLOBAL" else region_results.get(spec.key)
            if df is None:
                df = pd.DataFrame()
            if not emit_empty and _is_empty_df(df):
                continue  # 생성된 리소스가 없는 서비스는 문서(sheet) 생략
            excel.df_to_excel(writer, df, spec.sheet)
            written += 1
        if written == 0:
            # 모든 sheet 가 비어 전부 생략된 경우, 빈 워크북 방지용 안내 sheet 1개
            excel.df_to_excel(writer, pd.DataFrame([{"Info": "No resources found"}]), "summary")
            written = 1
    return written


def main():
    args = cmd_parse()

    # --init-config: 설정 파일만 생성하고 종료 (AWS 호출 없음)
    if args.init_config:
        init_config()
        return

    settings = global_config_init(args)
    klogger = awsglobal.klogger

    cwd = os.getcwd()
    prefix = args.output_filename or settings.get("output_prefix", "output")
    regions = resolve_regions(args, settings)
    global_region = settings.get("global_region", "us-east-1")
    # 실제 파일을 생성할 리전 (global_region 제외). 글로벌 리소스는 각 파일에 공통 포함.
    output_regions = resolve_output_regions(regions, global_region)
    # STS/credential 조회에 쓸 안전한 리전 (출력 리전 우선, 없으면 글로벌)
    probe_region = output_regions[0] if output_regions else global_region

    # account id 조회
    account_id = resolve_account_id(args.profile_name, probe_region)
    klogger.info("account: %s, 출력 리전: %s (글로벌 %s 리소스는 각 파일에 공통 포함), parallel: %s",
                 account_id, output_regions, global_region, args.parallel)

    # 병렬 시 SSO 안전: credential 선확정 + 만료 임박 폴백
    frozen = None
    parallel = args.parallel
    if parallel:
        frozen, remaining = freeze_credentials(args.profile_name, probe_region)
        threshold = settings.get("sso_min_remaining_minutes", 15)
        if remaining is not None and remaining < threshold:
            klogger.warning("credential 만료까지 %.1f분(임계 %d분) → 병렬 비활성, 순차 폴백",
                            remaining, threshold)
            parallel = False
            frozen = None

    factory = SessionFactory(args.profile_name, frozen)
    collector = Collector(
        factory, account_id, parallel=parallel,
        service_workers=settings.get("concurrency", {}).get("services", 8),
        disabled=settings.get("services", {}).get("disabled", []),
    )

    # Discovery(조합 방식 C) 설정. 기본 ON. --full / --no-discover 로 끌 수 있음.
    disc_cfg = settings.get("discovery", {}) or {}
    discovery_enabled = disc_cfg.get("enabled", True) and not (args.full or args.no_discover)
    emit_empty = disc_cfg.get("emit_empty_sheets", False) if discovery_enabled else True
    klogger.info("discovery: %s, emit_empty_sheets: %s",
                 "ON (없는 서비스 생략)" if discovery_enabled else "OFF (전량 수집)", emit_empty)

    # 변경 비교(diff) 설정. 기본 ON. --no-diff 로 끔.
    diff_cfg = settings.get("diff", {}) or {}
    diff_enabled = diff_cfg.get("enabled", True) and not args.no_diff

    ordered_specs = sorted(SERVICE_REGISTRY, key=lambda s: s.order)
    global_specs = [s for s in ordered_specs if s.scope == "GLOBAL"]
    regional_specs = [s for s in ordered_specs if s.scope == "REGIONAL"]

    # [0] Discovery - 글로벌/리전별 존재 서비스 집합 파악 (실패 시 None → 전량 폴백)
    global_discovered = None
    if discovery_enabled:
        klogger.info(">>> Discovery (글로벌 %s)", global_region)
        global_discovered = discover_services(
            CollectContext(factory, global_region, account_id, {}))

    # [1] 글로벌 리소스 1회 수집 (모든 리전 파일에 재사용)
    klogger.info(">>> 글로벌 리소스 수집 (%s)", global_region)
    global_results = collector.run(global_specs, global_region, discovered=global_discovered)

    # [2] 출력 리전별 수집 + 파일 출력 (글로벌 리소스는 매 파일에 공통 중복 포함)
    for region in output_regions:
        region_discovered = None
        if discovery_enabled:
            klogger.info(">>> Discovery (%s)", region)
            region_discovered = discover_services(
                CollectContext(factory, region, account_id, {}))
        klogger.info(">>> 리전 리소스 수집 (%s)", region)
        region_results = collector.run(regional_specs, region, discovered=region_discovered)
        out_path = build_output_path(prefix, account_id, region, cwd)

        # diff: 현재 파일을 쓰기 전에 '이전 리포트'를 먼저 찾아둔다.
        previous_path = None
        if diff_enabled:
            previous_path = diffreport.find_previous_report(out_path, prefix, account_id, region)

        n = write_excel(out_path, global_results, region_results, ordered_specs, emit_empty=emit_empty)
        klogger.info("생성 완료: %s (sheet %d개)", out_path, n)

        # diff: 이전 리포트가 있으면 변경 비교 엑셀 생성
        if diff_enabled:
            if previous_path:
                diff_name = f"diff_{account_id}_{region}_{datetime.now().strftime('%Y%m%d-%H%M')}.xlsx"
                diff_path = os.path.join(cwd, diff_name)
                try:
                    info = diffreport.build_diff(out_path, previous_path, diff_path)
                    klogger.info("변경 비교: %s → %s (%s)",
                                 os.path.basename(previous_path), os.path.basename(out_path),
                                 "변경 있음" if info["has_change"] else "변경 없음")
                except Exception as err:  # noqa: BLE001
                    klogger.warning("diff 생성 실패 region[%s]: %s", region, err)
            else:
                klogger.info("비교할 이전 리포트 없음 (region %s) → diff 생략", region)

    klogger.info("finished (파일 %d개 생성)", len(output_regions))


if __name__ == "__main__":
    main()
