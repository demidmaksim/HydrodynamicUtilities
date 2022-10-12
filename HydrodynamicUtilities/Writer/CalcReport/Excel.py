from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Tuple

from typing import Iterable

import xlsxwriter as xlsw
from HydrodynamicUtilities.Models.EclipseBinaryFile import SUMMARY
from HydrodynamicUtilities.Models.ParamVector import Interpolation, CumTimeSeriasParam
from HydrodynamicUtilities.Models.Time import TimeVector, generate_time_vector

import pandas as pd
import numpy as np
from copy import deepcopy


class ReportData:
    def __init__(
        self,
        well_names: List[str],
        group_names: List[str],
        calc_names: List[str],
    ) -> None:
        self.WellNames = well_names
        self.GroupNames = group_names
        self.CalcNames = calc_names


def get_all_names(summary: Iterable[SUMMARY]) -> Tuple[List[str], List[str]]:
    all_well_name = []
    all_grup_name = []

    for sum in summary:
        all_well_name.extend(sum.get_well_names())
        all_grup_name.extend(sum.get_group_name())

    return all_well_name, all_grup_name


def get_all_time(summary: Iterable[SUMMARY]) -> TimeVector:
    tv = deepcopy(summary[0].TimeVector)
    for sum in summary[1:]:
        tv.extend(sum.TimeVector)

    add_tv = generate_time_vector(tv.min, tv.max, "M", value_step=1)
    tv.extend(add_tv)
    return tv


def write_time(
    sheet: xlsw.workbook.Worksheet,
    book: xlsw.workbook.Workbook,
    tv: TimeVector,
    row: int,
    col: int,
) -> None:
    time_format = book.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})
    for tid, tp in enumerate(tv.to_datetime_list()):
        sheet.write_datetime(row + tid, col, tp, time_format)


def create_data_sheet(
    book: xlsw.Workbook,
    summary: Union[SUMMARY, Iterable[SUMMARY]],
) -> None:

    if isinstance(summary, SUMMARY):
        summary = [summary]

    target = {
        "OPT": "Нак. нефть",
        "WPT": "Нак. вода",
        "GPT": "Нак. газ",
        "OIT": "Нак. зак. нефти",
        "WIT": "Нак. зак. воды",
        "GIT": "Нак. зак. газа",
        "OMT": "Нак. мас. нефть",
        "WMT": "Нак. мас. вода",
        "GMT": "Нак. мас. газ",
        "WTT": "Нак. время работы",
    }
    sheet = book.add_worksheet("Data")
    tv = get_all_time(summary)
    write_time(sheet, book, tv, 5, 0)
    all_well_name, all_grup_name = get_all_names(summary)

    i = 1
    for sum in summary:
        for kw, kwl in target.items():
            for wn in all_well_name:
                wkw = f"W{kw}"
                sheet.write(0, i, i)
                sheet.write(1, i, sum.CalcName)
                sheet.write(2, i, wn)
                sheet.write(3, i, kwl)

                data = sum.get(wkw, wn)
                if data.shape[1] != 0:
                    sheet.write(4, i, data.Header.Unit[0])
                    ts = CumTimeSeriasParam(data.TimeVector, data.values)
                    value = ts.retime(tv)
                    sheet.write_column(5, i, value.values)
                i += 1

            for wn in all_grup_name:
                wkw = f"G{kw}"
                sheet.write(0, i, i)
                sheet.write(1, i, sum.CalcName)
                sheet.write(2, i, wn)
                sheet.write(3, i, kwl)
                sheet.write(4, i, "---")
                data = sum.get(wkw, wn)
                if data.shape[1] != 0:
                    ts = CumTimeSeriasParam(data.TimeVector, data.values)
                    value = ts.retime(tv)
                    sheet.write_column(5, i, value.values)
                i += 1


def create_object_sheet(
    book: xlsw.Workbook,
    summary: Union[SUMMARY, Iterable[SUMMARY]],
) -> None:

    target = {
        "OPT": "Нак. нефть",
        "WPT": "Нак. вода",
        "GPT": "Нак. газ",
        "OIT": "Нак. зак. нефти",
        "WIT": "Нак. зак. воды",
        "GIT": "Нак. зак. газа",
        "OMT": "Нак. мас. нефть",
        "WMT": "Нак. мас. вода",
        "GMT": "Нак. мас. газ",
        "WTT": "Нак. время работы",
    }

    if isinstance(summary, SUMMARY):
        summary = [summary]

    sheet = book.add_worksheet("Objects")
    all_well_name, all_grup_name = get_all_names(summary)
    names = all_well_name + all_grup_name
    sheet.write_row(0, 4, names)

    tv = get_all_time(summary)
    tv = generate_time_vector(tv.min, tv.max, "M", value_step=1)
    write_time(sheet, book, tv, 2, 3)

    name = []
    for sum in summary:
        name.append(sum.CalcName)

    sheet.write(2, 0, "Model")
    sheet.write(3, 0, "Parameter")
    sheet.write(4, 0, "Multiplier")
    # sheet.write(3, 0, "Multiplier")

    tar = [
        "Добыча воды",
        "Добыча газа",
        "Закачка воды",
        "Закачка газа",
        "Добыча нефти",
        "Время работы",
        "Дебит воды",
        "Дебит нефти",
        "Дебит газа",
        "Приемистость воды",
        "Приемистость газа",
        "Накопл. вода",
        "Накопл. газ",
        "Накопл. закачка воды",
        "Накопл. закачка газа",
        "Накопл. массовая добыча нефти",
        "Накопленное время работы",
    ]
    mul = [" ", "тыс.", "млн.", "млрд."]

    sheet.write(2, 1, name[0])
    sheet.write(3, 1, tar[0])
    sheet.write(4, 0, "")

    sheet.data_validation("B3", {"validate": "list", "source": name})
    sheet.data_validation("B4", {"validate": "list", "source": tar})
    sheet.data_validation("B5", {"validate": "list", "source": mul})

    r = (
        "=("
        "    VLOOKUP("
        "         INDEX("
        "                $1:$1048576,"
        "                ROW()+1,"
        "                4"
        "               ),"
        "         Data!$1:$1048576,"
        "         1+SUMIFS("
        "                Data!$1:$1,"
        "                Data!$2:$2,"
        "                $B$3,"
        "                Data!$3:$3,"
        "                INDEX($1:$1,COLUMN()),"
        "                Data!$4:$4,"
        "                VLOOKUP("
        "                    $B$4,"
        "                    TL!$1:$1048576,"
        "                    2,"
        "                    False"
        "                   )"
        "               ),"
        "         False"
        "       )"
        "    -VLOOKUP("
        "         INDEX("
        "                $1:$1048576,"
        "                ROW(),"
        "                4"
        "               ),"
        "         Data!$1:$1048576,"
        "         1+SUMIFS("
        "                Data!$1:$1,"
        "                Data!$2:$2,"
        "                $B$3,"
        "                Data!$3:$3,"
        "                INDEX($1:$1,COLUMN()),"
        "                Data!$4:$4,"
        "                VLOOKUP("
        "                    $B$4,"
        "                    TL!$1:$1048576,"
        "                    2,"
        "                    False"
        "                   )"
        "               ),"
        "         False"
        "       )"
        "    *IF("
        "         VLOOKUP("
        "             $B$4,"
        "             TL!$1:$1048576,"
        "             3,"
        "             False"
        '             )="Тотал",'
        "         0,"
        "         1"
        "        )"
        ")"
        "/IF("
        '       $B$5="млрд.",'
        "       10^9,"
        "       IF("
        '           $B$5="млн.",'
        "           10^6,"
        "           IF("
        '               $B$5="тыс.",'
        "               10^3,"
        "               1"
        "              )"
        "         )"
        ")"
        "/IF("
        "       VLOOKUP("
        "              $B$4,"
        "              TL!$1:$1048576,"
        "              3,"
        "              False"
        '          )="Расход",'
        "          INDEX("
        "                $1:$1048576,"
        "                ROW()+1,"
        "                4"
        "               )"
        "          -INDEX("
        "                $1:$1048576,"
        "                ROW(),"
        "                4"
        "               ),"
        "       1"
        ")"
    )
    res = r.replace(" ", "")
    for col in range(len(names)):
        for row in range(len(tv.to_datetime64())):
            sheet.write_formula(row + 2, col + 4, res)


def create_tl(
    book: xlsw.Workbook,
    summary: Union[SUMMARY, Iterable[SUMMARY]],
):
    data = [
        ["Добыча воды", "Нак. вода", "Период"],
        ["Добыча газа", "Нак. газ", "Период"],
        ["Закачка воды", "Нак. зак. воды", "Период"],
        ["Закачка газа", "Нак. зак. газа", "Период"],
        ["Добыча нефти", "Нак. мас. нефть", "Период"],
        ["Время работы", "Нак. время работы", "Период"],
        ["Дебит воды", "Нак. вода", "Расход"],
        ["Дебит нефти", "Нак. мас нефть", "Расход"],
        ["Дебит газа", "Нак. газ", "Расход"],
        ["Приемистость воды", "Нак. зак воды", "Расход"],
        ["Приемистость газа", "Нак. зак газа", "Расход"],
        ["Накопл. вода", "Нак. вода", "Тотал"],
        ["Накопл. газ", "Нак. газ", "Тотал"],
        ["Накопл. закачка воды", "Нак. зак. воды", "Тотал"],
        ["Накопл. закачка газа", "Нак. зак. газа", "Тотал"],
        ["Накопл. массовая добыча нефти", "Нак. мас. нефть", "Тотал"],
        ["Накопленное время работы", "Нак. время работы", "Тотал"],
    ]
    sheet = book.add_worksheet("TL")
    for rid, row in enumerate(data):
        sheet.write_row(rid, 0, row)


def create(summary: SUMMARY):
    book = xlsw.Workbook("Test.xlsx")
    create_data_sheet(book, summary)
    create_tl(book, summary)
    create_object_sheet(book, summary)
    book.close()
