####################################################################################################
#
# Purpose   : compare previous vs current AWS report (xlsx) and emit a change(diff) report
# Source    : diffreport.py
# Usage     : from kskpkg import diffreport
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create
#
# 비교 방식:
#   - sheet(리소스 유형)별로 SHEET_KEY_COLUMNS 의 key 컬럼으로 이전/현재 행을 매칭.
#   - Added(신규) / Removed(삭제) / Modified(값 변경, 바뀐 컬럼만) 분류.
#   - key 컬럼이 없거나 데이터에 없으면 전체 행 비교(추가/삭제 위주)로 폴백.
#   - 결과: Summary sheet(변경 유무/건수) + 'chg_<sheet>' 변경 상세 sheet.
####################################################################################################
from __future__ import annotations

import glob
import os
import re

import pandas as pd

from . import excel
from .config import awsglobal
from .registry import SHEET_KEY_COLUMNS

klogger = awsglobal.klogger

# 비교에서 제외할 컬럼(값이 매번 달라지는 메타성 컬럼 등)
_IGNORE_COLUMNS = {"Region"}
# placeholder(빈 데이터) 판정값
_PLACEHOLDERS = {"", " ", "nan", "None"}


def find_previous_report(current_path: str, prefix: str, account_id: str, region: str) -> str | None:
    """현재 리포트와 같은 account/region/prefix 의 '가장 최근 이전 파일'을 찾는다.

    파일명 규칙: <prefix>_<account>_<region>_<YYYYmmdd-HHMM>.xlsx
    현재 파일은 제외하고, 타임스탬프가 가장 큰(=직전) 파일을 반환.
    """
    folder = os.path.dirname(os.path.abspath(current_path))
    pattern = os.path.join(folder, f"{prefix}_{account_id}_{region}_*.xlsx")
    candidates = [p for p in glob.glob(pattern)
                  if os.path.abspath(p) != os.path.abspath(current_path)
                  and not os.path.basename(p).startswith("diff_")]
    if not candidates:
        return None
    # 파일명 타임스탬프 기준 정렬 (없으면 mtime)
    def _ts(path):
        m = re.search(r"_(\d{8}-\d{4})\.xlsx$", os.path.basename(path))
        return m.group(1) if m else ""
    candidates.sort(key=lambda p: (_ts(p), os.path.getmtime(p)))
    return candidates[-1]


def _read_workbook(path: str) -> dict[str, pd.DataFrame]:
    """리포트 xlsx 를 {sheet: DataFrame} 로 로드.

    각 sheet 는 df_to_excel 가 startrow=2(제목/헤더 포함)로 기록했으므로
    header 행(3번째, 0-index 2)을 헤더로 읽는다.
    """
    result = {}
    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
    except Exception as err:  # noqa: BLE001
        klogger.error("diff: 이전 리포트 로드 실패 %s: %s", path, err)
        return result
    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet, header=2, engine="openpyxl")
            # remark 꼬리행 제거: 전부 NaN 이거나 'Remark:' 로 시작하는 행 컷
            df = df.dropna(how="all")
            if not df.empty and df.iloc[:, 0].astype(str).str.startswith("Remark:").any():
                cut = df.index[df.iloc[:, 0].astype(str).str.startswith("Remark:")][0]
                df = df.loc[: cut - 1]
            result[sheet] = df.reset_index(drop=True)
        except Exception as err:  # noqa: BLE001
            klogger.warning("diff: sheet '%s' 로드 건너뜀: %s", sheet, err)
    return result


def _norm(v) -> str:
    s = str(v).strip()
    return "" if s in _PLACEHOLDERS else s


def _row_key(row: pd.Series, key_cols: list[str]) -> str:
    return "||".join(_norm(row.get(c, "")) for c in key_cols)


def _row_signature(row: pd.Series, compare_cols: list[str]) -> str:
    return "~~".join(f"{c}={_norm(row.get(c, ''))}" for c in compare_cols)


def _diff_sheet(sheet: str, prev: pd.DataFrame, curr: pd.DataFrame) -> list[dict]:
    """한 sheet 의 변경 행 목록 반환."""
    changes = []
    key_cols = [c for c in SHEET_KEY_COLUMNS.get(sheet, []) if
                (prev is None or c in prev.columns) and (curr is None or c in curr.columns)]
    prev = prev if prev is not None else pd.DataFrame()
    curr = curr if curr is not None else pd.DataFrame()

    # 비교 대상 컬럼(양쪽 공통, ignore 제외)
    common_cols = [c for c in curr.columns if c in prev.columns and c not in _IGNORE_COLUMNS]

    if not key_cols:
        # 폴백: 전체 행 시그니처로 추가/삭제만
        sig_cols = common_cols or list(curr.columns)
        prev_sigs = {_row_signature(r, sig_cols) for _, r in prev.iterrows()} if not prev.empty else set()
        curr_sigs = {_row_signature(r, sig_cols) for _, r in curr.iterrows()} if not curr.empty else set()
        for _, r in curr.iterrows():
            if _row_signature(r, sig_cols) not in prev_sigs:
                changes.append({"ChangeType": "Added", "Key": "(row)", "ChangedColumns": " ",
                                "Before": " ", "After": _row_signature(r, sig_cols)[:300]})
        for _, r in prev.iterrows():
            if _row_signature(r, sig_cols) not in curr_sigs:
                changes.append({"ChangeType": "Removed", "Key": "(row)", "ChangedColumns": " ",
                                "Before": _row_signature(r, sig_cols)[:300], "After": " "})
        return changes

    prev_map = {_row_key(r, key_cols): r for _, r in prev.iterrows()} if not prev.empty else {}
    curr_map = {_row_key(r, key_cols): r for _, r in curr.iterrows()} if not curr.empty else {}
    # 빈 key(모두 placeholder) 는 '데이터 없음' 으로 보고 제외
    prev_map = {k: v for k, v in prev_map.items() if k.replace("|", "").strip()}
    curr_map = {k: v for k, v in curr_map.items() if k.replace("|", "").strip()}

    # Added / Modified
    for k, cr in curr_map.items():
        if k not in prev_map:
            changes.append({"ChangeType": "Added", "Key": k, "ChangedColumns": " ",
                            "Before": " ", "After": " "})
        else:
            pr = prev_map[k]
            diffs = []
            for c in common_cols:
                if _norm(pr.get(c, "")) != _norm(cr.get(c, "")):
                    diffs.append(c)
            if diffs:
                before = "; ".join(f"{c}={_norm(pr.get(c, ''))}" for c in diffs)[:300]
                after = "; ".join(f"{c}={_norm(cr.get(c, ''))}" for c in diffs)[:300]
                changes.append({"ChangeType": "Modified", "Key": k,
                                "ChangedColumns": ", ".join(diffs), "Before": before, "After": after})
    # Removed
    for k in prev_map:
        if k not in curr_map:
            changes.append({"ChangeType": "Removed", "Key": k, "ChangedColumns": " ",
                            "Before": " ", "After": " "})
    return changes


def build_diff(current_path: str, previous_path: str, out_path: str) -> dict:
    """이전/현재 리포트를 비교해 diff 엑셀 생성. 요약 dict 반환."""
    prev_wb = _read_workbook(previous_path)
    curr_wb = _read_workbook(current_path)
    all_sheets = sorted(set(prev_wb) | set(curr_wb))

    summary_rows = []
    sheet_changes: dict[str, list[dict]] = {}
    total = 0
    for sheet in all_sheets:
        changes = _diff_sheet(sheet, prev_wb.get(sheet), curr_wb.get(sheet))
        added = sum(1 for c in changes if c["ChangeType"] == "Added")
        removed = sum(1 for c in changes if c["ChangeType"] == "Removed")
        modified = sum(1 for c in changes if c["ChangeType"] == "Modified")
        if changes:
            sheet_changes[sheet] = changes
            total += len(changes)
        summary_rows.append({
            "Resource(Sheet)": sheet,
            "Changed": "Y" if changes else "N",
            "Added": added, "Removed": removed, "Modified": modified,
        })

    has_change = total > 0
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        # Summary 맨 앞
        summary_df = pd.DataFrame(summary_rows) if summary_rows else \
            pd.DataFrame([{"Resource(Sheet)": " ", "Changed": " ", "Added": 0, "Removed": 0, "Modified": 0}])
        # 헤더에 전체 변경 유무 표시행 추가
        overview = pd.DataFrame([{
            "Item": "Change Detected", "Value": "YES" if has_change else "NO"},
            {"Item": "Previous Report", "Value": os.path.basename(previous_path)},
            {"Item": "Current Report", "Value": os.path.basename(current_path)},
            {"Item": "Total Changes", "Value": total},
        ])
        excel.df_to_excel(writer, overview, "Summary")
        excel.df_to_excel(writer, summary_df, "ChangeCountBySheet")
        # 변경 상세 (변경 있는 sheet 만)
        for sheet, changes in sheet_changes.items():
            name = ("chg_" + sheet)[:31]
            excel.df_to_excel(writer, pd.DataFrame(changes), name)

    klogger.info("diff 생성: %s (변경 %s, 총 %d건)", out_path, "있음" if has_change else "없음", total)
    return {"has_change": has_change, "total": total, "out_path": out_path}
