from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Tuple

from typing import Iterable

import xlsxwriter as xlsw
from pathlib import Path
from HydrodynamicUtilities.Models.EclipseBinaryFile import SUMMARY
from HydrodynamicUtilities.Models.ParamVector import CumTimeSeriasParam
from HydrodynamicUtilities.Models.Time import TimeVector, generate_time_vector

from .ExcelFormula import formula

import pandas as pd
from copy import deepcopy


class ReportData:

    sheet_data = (
        ("OPT", "Нак. нефть"),
        ("OVPT", "Нак. пл. нефть"),
        ("OIT", "Нак. зак. нефти"),
        ("OVIT", "Нак. пл. вода"),

        ("WPT", "Нак. вода"),
        ("WVPT", "Нак. пл. вода"),
        ("WIT", "Нак. зак. воды"),
        ("WVIT", "Нак. пл. вода"),

        ("GPT", "Нак. газ"),
        ("GVPT", "Нак. пл. газа"),
        ("GIT", "Нак. зак. газа"),
        ("GVIT", "Нак. пл. газа"),

        ("WTT", "Нак. время работы"),

        ("BHP", "Забойное давление"),
        ("THP", "Устьевое давление"),
    )

    data = [
        ["Накопл. нефть", "Нак. нефть", "Тотал"],
        ["Добыча нефти", "Нак. нефть", "Период"],
        ["Дебит нефти", "Нак. нефть", "Расход"],
        ["Упл. Дебит дебит", "Нак. нефть", "Упл. Расход"],

        ["Накопл. вода", "Нак. газ", "Тотал"],
        ["Добыча воды", "Нак. вода", "Период"],
        ["Дебит воды", "Нак. вода", "Расход"],
        ["Упл. Дебит воды", "Нак. вода", "Упл. Расход"],

        ["Накопл. газ", "Нак. газ", "Тотал"],
        ["Добыча газа", "Нак. газ", "Период"],
        ["Дебит газа", "Нак. газ", "Расход"],
        ["Упл. Дебит газа", "Нак. газ", "Упл. Расход"],

        ["Накопл. закачка воды", "Нак. зак. воды"],
        ["Закачка воды", "Нак. зак. воды", "Период"],
        ["Приемистость воды", "Нак. зак воды", "Расход"],
        ["Упл. Приемистость воды", "Нак. зак воды", "Упл. Расход"],

        ["Накопл. закачка газа", "Нак. зак. газа", "Тотал"],
        ["Закачка газа", "Нак. зак. газа", "Период"],
        ["Приемистость газа", "Нак. зак газа", "Расход"],
        ["Упл. Приемистость газа", "Нак. зак газа", "Упл. Расход"],

        ["Накопленное время работы", "Нак. время работы", "Тотал"],
        ["Время работы", "Нак. время работы", "Период"],
        ["Коэффициент эксплуатации", "Нак. время работы", "Расход"],

        ["Забойное давление", "Забойное давление", "Тотал"],
        ["Устьевое давление", "Устьевое давление", "Тотал"],

        ["Газовый фактор", "Нак. газ", "Период", "Нак. нефть", "Период"],
        ["Обводненность", "Нак. вода", "Период", "Нак. нефть", "Период"],

        ["Компенсация", "Нак. вода", "Период", "Нак. нефть", "Период"],
        ["Нак. Компенсация", "Нак. вода", "Тотал", "Нак. нефть", "Тотал"],

        ["Накопл. пл. нефть", "Нак. пл. нефть", "Тотал"],
        ["Добыча пл. нефти", "Нак. пл. нефть", "Период"],
        ["Дебит пл. нефти", "Нак.  пл. нефть", "Расход"],
        ["Упл. пл. Дебит дебит", "Нак.  пл. нефть", "Упл. Расход"],

        ["Накопл. пл. нефть", "Нак. пл. вода", "Тотал"],
        ["Добыча пл. воды", "Нак. пл. воды", "Период"],
        ["Дебит пл. воды", "Нак.  пл. воды", "Расход"],
        ["Упл. Дебит пл. воды", "Нак. пл. воды", "Упл. Расход"],

        ["Накопл. пл. газ", "Нак. пл. газ", "Тотал"],
        ["Добыча пл. газа", "Нак. пл. газ", "Период"],
        ["Дебит пл. газа", "Нак. пл. газ", "Расход"],
        ["Упл. пл. Дебит газа", "Нак. пл. газ", "Упл. Расход"],

        ["Накопл. закачка воды", "Нак. зак. воды"],
        ["Закачка воды", "Нак. зак. воды", "Период"],
        ["Приемистость воды", "Нак. зак воды", "Расход"],
        ["Упл. Приемистость воды", "Нак. зак воды", "Упл. Расход"],

        ["Накопл. закачка газа", "Нак. зак. газа", "Тотал"],
        ["Закачка газа", "Нак. зак. газа", "Период"],
        ["Приемистость газа", "Нак. зак газа", "Расход"],
        ["Упл. Приемистость газа", "Нак. зак газа", "Упл. Расход"],

    ]

    def __init__(
        self,
        well_names: List[str],
        group_names: List[str],
        calc_names: List[str],
    ) -> None:
        self.WellNames = well_names
        self.GroupNames = group_names
        self.CalcNames = calc_names

    @staticmethod
    def get_all_time(summary: List[SUMMARY]) -> TimeVector:
        tv = deepcopy(summary[0].TimeVector)
        for sum in summary[1:]:
            tv.extend(sum.TimeVector)

        return generate_time_vector(tv.min, tv.max, "M", value_step=1)

    @staticmethod
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

    def get_all_names(self) -> List[str]:
        return list(self.WellNames) + list(self.GroupNames)


def get_report_data(summary: Iterable[SUMMARY]) -> ReportData:
    well_names = []
    group_names = []
    calc_names = []
    for su in summary:
        calc_names.append(su.CalcName)
        well_names.extend(su.get_well_names())
        group_names.extend(su.get_group_name())
    return ReportData(
        pd.unique(well_names),
        pd.unique(group_names),
        pd.unique(calc_names),
    )


def __write(
        model: SUMMARY,
        model_kw_name: str,
        kw_name: str,
        sheet: xlsw.workbook.Worksheet,
        tv: TimeVector,
        for_iter: List[str],
        i: int,
) -> int:
    for wn in for_iter:
        sheet.write(0, i, i)
        sheet.write(1, i, model.CalcName)
        sheet.write(2, i, wn)
        sheet.write(3, i, kw_name)
        data = model.get(model_kw_name, wn)
        if data.shape[1] != 0 and model_kw_name not in ("GBHP", "GTHP"):
            sheet.write(4, i, data.Header.Unit[0])
            ts = CumTimeSeriasParam(data.TimeVector, data.Values)
            value = ts.retime(tv)
            sheet.write_column(5, i, value.values)
            i += 1
    return i


def write_formula(
        model: SUMMARY,
        model_kw_name: str,
        kw_name: str,
        sheet: xlsw.workbook.Worksheet,
        tv: TimeVector,
        for_iter: List[str],
        i: int,
) -> int:
    for wn in for_iter:
        sheet.write(0, i, i)
        sheet.write(1, i, model.CalcName)
        sheet.write(2, i, wn)
        sheet.write(3, i, kw_name)
        data = model.get(model_kw_name, wn)
        if data.shape[1] != 0 and model_kw_name not in ("GBHP", "GTHP"):
            sheet.write(4, i, data.Header.Unit[0])
            ts = CumTimeSeriasParam(data.TimeVector, data.Values)
            value = ts.retime(tv)
            sheet.write_column(5, i, value.values)
            i += 1
    return i


def fill_data_sheet(
        setting: ReportData,
        book: xlsw.Workbook,
        summary: List[SUMMARY],
        tv: TimeVector,
) -> None:
    sheet = book.add_worksheet("Data")
    setting.write_time(sheet, book, tv, 5, 0)
    i = 1
    wnames = setting.WellNames
    gnames = setting.WellNames
    for model in summary:
        for kw, kw_name in setting.sheet_data:
            i = __write(model, f"W{kw}", kw_name, sheet, tv, wnames, i)
            i = __write(model, f"G{kw}", kw_name, sheet, tv, gnames, i)


def fill_technical_list(
        setting: ReportData,
        book: xlsw.Workbook,
) -> None:
    sheet = book.add_worksheet("TechnicalList")
    for rid, row in enumerate(setting.data):
        sheet.write_row(rid, 0, row)

    sheet.write_column(0, 10, [" ", "тыс.", "млн.", "млрд."])
    sheet.write_column(0, 11, [1, 10**3, 10**6, 10**9])


def create_object_sheet(
        setting: ReportData,
        book: xlsw.Workbook,
        summary: List[SUMMARY],
        tv: TimeVector,
) -> None:
    sheet = book.add_worksheet("Objects")
    sheet.write_row(0, 4, setting.get_all_names())
    setting.write_time(sheet, book, tv, 2, 3)

    name = []
    for sum in summary:
        name.append(sum.CalcName)

    sheet.write(2, 0, "Model")
    sheet.write(3, 0, "Parameter")
    sheet.write(4, 0, "Multiplier")
    # sheet.write(3, 0, "Multiplier")

    mul = [" ", "тыс.", "млн.", "млрд."]

    sheet.write(2, 1, name[0])
    sheet.write(3, 1, "")
    sheet.write(4, 0, "")

    sheet.data_validation("B3", {"validate": "list", "source": name})
    sheet.data_validation("B4", {"validate": "list", "source": f"TechnicalList!A1:A{len(setting.data)}"})
    sheet.data_validation("B5", {"validate": "list", "source": "TechnicalList!K1:K4"})

    for col in range(len(setting.get_all_names())):
        for row in range(len(tv.to_datetime64())):
            sheet.write_formula(row + 2, col + 4, formula)


def create(
        path: Union[Path, str],
        summary: Iterable[SUMMARY]
) -> None:

    if isinstance(summary, SUMMARY):
        summary = [summary]
    else:
        summary = list(summary)

    setting = get_report_data(summary)
    tv = setting.get_all_time(summary)
    book = xlsw.Workbook(path)
    fill_data_sheet(setting, book, summary, tv)
    fill_technical_list(setting, book)
    create_object_sheet(setting, book, summary, tv)
    book.close()


