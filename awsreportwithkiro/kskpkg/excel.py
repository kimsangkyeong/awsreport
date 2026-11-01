####################################################################################################
#
# Purpose   : DataFrame -> styled Excel sheet writer
# Source    : excel.py
# Usage     : from kskpkg import excel
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py df_to_excel)
#
# Ref     : https://xlsxwriter.readthedocs.io/index.html
####################################################################################################
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


def df_to_excel(writer, df: pd.DataFrame, sheetname: str) -> None:
    """DataFrame 을 스타일(제목/헤더색/컬럼폭/셀병합/remark)과 함께 sheet 로 출력.

    기존 awsreport.df_to_excel 의 서식 로직을 계승한다.
    Excel sheet 이름은 31자 제한이 있어 잘라낸다.
    """
    sheetname = sheetname[:31]
    if df is None:
        df = pd.DataFrame()

    df.to_excel(writer, sheet_name=sheetname, startrow=2, index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheetname]

    # 제목
    worksheet.write(
        0, 0, f"[ {sheetname} ]",
        workbook.add_format({"bold": True, "color": "#E26B0A", "size": 14}),
    )

    if df.empty:
        worksheet.write(2, 0, "(No Data)")
        worksheet.write(4, 0, "Remark:", workbook.add_format({"bold": True}))
        worksheet.write(5, 0, "The last update time is " + datetime.now().strftime("%Y-%m-%d %H:%M") + ".")
        return

    # 헤더 서식
    header_format = workbook.add_format({
        "bold": True, "align": "center", "valign": "vcenter",
        "font_size": 10, "text_wrap": True, "fg_color": "#D9D9D9", "border": 1,
    })
    col_width_list = []
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(2, col_num, value, header_format)
        col_width_list.append(12)

    for col, colwidth in enumerate(col_width_list):
        worksheet.set_column(col, col + 1, colwidth)

    # 데이터 서식 + 컬럼폭 자동 조정
    data_format = workbook.add_format({
        "align": "left", "valign": "vcenter", "text_wrap": True, "font_size": 9, "border": 1,
    })
    row_idx, col_idx = df.shape
    for row in range(row_idx):
        for col in range(col_idx):
            value = df.values[row, col]
            if isinstance(value, dict):
                data_len = np.ceil(len(str(value)) / 4)
                if col_width_list[col] < data_len:
                    col_width_list[col] = 100 if data_len >= 100 else data_len
                    worksheet.set_column(col, col + 1, col_width_list[col])
                worksheet.write(row + 3, col, str(value), data_format)
            elif isinstance(value, str):
                data_len = len(value)
                if col_width_list[col] < data_len:
                    if data_len >= 60:
                        col_width_list[col] = 50
                    elif data_len >= 40:
                        col_width_list[col] = 40
                    elif data_len >= 30:
                        col_width_list[col] = 25
                    else:
                        col_width_list[col] = data_len
                    worksheet.set_column(col, col + 1, col_width_list[col])
                worksheet.write(row + 3, col, value, data_format)
            elif isinstance(value, (list, tuple)):
                worksheet.write(row + 3, col, str(value), data_format)
            else:
                worksheet.write(row + 3, col, value, data_format)

    # column 'A' 동일값 셀 병합
    merge_format = workbook.add_format({
        "font_size": 9, "border": 1, "align": "left", "valign": "vcenter", "text_wrap": True,
    })
    col = 0
    befdata = ""
    startrow = 0
    currrow = 0
    for row in range(row_idx):
        currrow = row
        if befdata == df.values[row, col]:
            continue
        if befdata != "" and (row - startrow >= 2):
            worksheet.merge_range(
                f"A{startrow + 4}:A{(row - 1) + 4}",
                str(befdata) if isinstance(befdata, dict) else befdata,
                merge_format,
            )
        startrow = row
        befdata = df.values[row, col]
    if currrow - startrow >= 1:  # 마지막 병합
        worksheet.merge_range(
            f"A{startrow + 4}:A{currrow + 4}",
            str(befdata) if isinstance(befdata, dict) else befdata,
            merge_format,
        )

    # remark
    worksheet.write(len(df) + 4, 0, "Remark:", workbook.add_format({"bold": True}))
    worksheet.write(len(df) + 5, 0, "The last update time is " + datetime.now().strftime("%Y-%m-%d %H:%M") + ".")
