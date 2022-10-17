from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Tuple, Optional, Dict

from typing import Iterable

import numpy as np
import pandas as pd

import xlsxwriter as xlsw
from pathlib import Path
from HydrodynamicUtilities.Models.EclipseBinaryFile import SUMMARY
from HydrodynamicUtilities.Models.ParamVector import (
    CumTimeSeriasParam,
    RateTimeSeriasParam,
    TimeSeries,
)
from HydrodynamicUtilities.Models.Time import (
    TimeVector,
    generate_time_vector,
    TimePoint,
)

from copy import deepcopy

import abc


class KeywordReport:
    Print = False
    Name = ""
    WellFlag = False
    GroupFlag = False
    Mylti = 1
    MyltiName = ""
    Unit = "---"

    @abc.abstractmethod
    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        pass

    def get_well(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
    ) -> Optional[np.ndarray]:
        return self.get(name, summary, tv, "W")

    def get_group(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
    ) -> Optional[np.ndarray]:
        return self.get(name, summary, tv, "G")

    def get_unit(self) -> str:
        if self.MyltiName != "":
            return f"{self.MyltiName} {self.Unit}"
        else:
            return self.Unit


class CumWrite(KeywordReport):
    def __init__(
        self,
        mnemonic: str,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        summary = summary.get(f"{otype}{self.Mnemonc}", name)
        if summary.shape[1] != 1:
            return None
        ts = CumTimeSeriasParam(summary.TimeVector, summary.Values)
        value = ts.retime(tv)
        return value.values


class WTT(KeywordReport):
    def __init__(
        self,
        mnemonic: str,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        try_summary = summary.get(f"{otype}{self.Mnemonc}", name)

        if try_summary.shape[1] != 1:
            try:
                tot_mn = ("WOPT", "WWPT", "WGPT", "WOIT", "WWIT", "WGIT")
                rat_mn = ("WOPR", "WWPR", "WGPR", "WOIR", "WWIR", "WGIR")
                for tot, rat in zip(tot_mn, rat_mn):
                    op = summary.get(tot, name).to_cum_time_series()
                    dop = op.get_delta_serias()
                    op = summary.get(rat, name).to_rate_time_series()
                    op[op.values == 0] = 1
                    top = dop.values[:-1] / op.values[1:]
                    if sum(top) > 0:
                        top = np.concatenate((top, [top[-1]]))
                        ts = RateTimeSeriasParam(summary.TimeVector, top)
                        ts = ts.get_cum_series()
                        return ts.retime(tv).values

                    if tot == "WGIT":
                        top = np.concatenate((top, [top[-1]]))
                        ts = RateTimeSeriasParam(summary.TimeVector, top)
                        ts = ts.get_cum_series()
                        return ts.retime(tv).values

            except ValueError:
                return None

        if try_summary.shape[1] != 1:
            return None

        ts = CumTimeSeriasParam(try_summary.TimeVector, try_summary.Values)
        value = ts.retime(tv)
        return value.values


class FlowWrite(KeywordReport):
    def __init__(
        self,
        mnemonic: str,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        summary = summary.get(f"{otype}{self.Mnemonc}", name)
        if summary.shape[1] != 1:
            return None
        ts = TimeSeries(summary.TimeVector, summary.Values)
        tsm = ts.to_interpolation_model()
        value = tsm.get_value(tv)
        return value.values


class FPCWrite(KeywordReport):
    # FlowPeriodCalcWrite
    def __init__(
        self,
        mnemonic: str,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        summary = summary.get(f"{otype}{self.Mnemonc}", name)
        if summary.shape[1] != 1:
            return None
        ts = CumTimeSeriasParam(summary.TimeVector, summary.Values)
        tsm = ts.to_interpolation_model(
            bounds_error=False,
            fill_value=(min(ts.values), max(ts.values)),
        )
        # value = ts.retime(tv)
        results = tsm.get_delta(tv)
        return results.values


class WaterCut(KeywordReport):
    def __init__(
        self,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        ws = summary.get(f"{otype}WPT", name)
        ls = summary.get(f"{otype}LPT", name)

        if ls.shape[0] != 0:
            os = summary.get(f"{otype}OPT", name)
            ls.Values = ws.Values + os.Values

        if ws.shape[1] != 1 or ls.shape[1] != 1:
            return None

        wtts = CumTimeSeriasParam(ws.TimeVector, ws.Values)
        ltts = CumTimeSeriasParam(ls.TimeVector, ls.Values)
        wtts = wtts.retime(tv)
        ltts = ltts.retime(tv)
        wrts = wtts.get_delta_serias()
        lrts = ltts.get_delta_serias()
        wrts[wrts.values == 0] = 0
        lrts[lrts.values == 0] = 1
        value = wrts / lrts
        return value.values


class GOR(KeywordReport):
    def __init__(
        self,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        ws = summary.get(f"{otype}GPT", name)
        ls = summary.get(f"{otype}OPT", name)

        if ws.shape[1] != 1 or ls.shape[1] != 1:
            return None

        wtts = CumTimeSeriasParam(ws.TimeVector, ws.Values)
        ltts = CumTimeSeriasParam(ls.TimeVector, ls.Values)
        wtts = wtts.retime(tv)
        ltts = ltts.retime(tv)
        wrts = wtts.get_delta_serias()
        lrts = ltts.get_delta_serias()
        wrts[wrts.values == 0] = 0
        lrts[lrts.values == 0] = 1
        value = wrts / lrts
        return value.values


class Compensation(KeywordReport):
    def __init__(
        self,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        ws = summary.get(f"{otype}VPT", name)
        ls = summary.get(f"{otype}VIT", name)

        if ws.shape[1] != 1 or ls.shape[1] != 1:
            return None

        wtts = CumTimeSeriasParam(ws.TimeVector, ws.Values)
        ltts = CumTimeSeriasParam(ls.TimeVector, ls.Values)
        wtts = wtts.retime(tv)
        ltts = ltts.retime(tv)
        wrts = wtts.get_delta_serias()
        lrts = ltts.get_delta_serias()
        wrts[wrts.values == 0] = 0
        lrts[lrts.values == 0] = 1
        value = wrts / lrts
        return value.values


class CumComp(KeywordReport):
    def __init__(
        self,
        name: str,
        unit: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
        mylti: Union[float, int] = 1,
        mylti_name: str = "",
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag
        self.Mylti = mylti
        self.MyltiName = mylti_name
        self.Unit = unit

    def get(
        self,
        name: str,
        summary: SUMMARY,
        tv: TimeVector,
        otype: str,
    ) -> Optional[np.ndarray]:
        ws = summary.get(f"{otype}VIT", name)
        ls = summary.get(f"{otype}VPT", name)

        if ws.shape[1] != 1 or ls.shape[1] != 1:
            return None

        wtts = CumTimeSeriasParam(ws.TimeVector, ws.Values)
        ltts = CumTimeSeriasParam(ls.TimeVector, ls.Values)
        wtts = wtts.retime(tv)
        ltts = ltts.retime(tv)
        wtts[wtts.values == 0] = 0
        ltts[ltts.values == 0] = 1
        value = wtts / ltts
        return value.values


class Request:
    __OPT = "Нак. нефть"
    __WPT = "Нак. вода"
    __GPT = "Нак. газ"

    __OIT = "Нак. зак. нефть"
    __WIT = "Нак. зак. воды"
    __GIT = "Нак. зак. газ"

    __OVPT = "Нак. нефть (пл. усл.)"
    __WVPT = "Нак. воды (пл. усл.)"
    __GVPT = "Нак. газ (пл. усл.)"

    __OVIT = "Нак. зак. нефти (п.у.)"
    __WVIT = "Нак. зак. воды (п.у.)"
    __GVIT = "Нак. зак. газа (п.у.)"

    __BP9 = "WBP9"
    __BHP = "Забойное давление"
    __THP = "Устьевое давление"

    __OPR = "Добыча нефти"
    __WPR = "Добыча воды"
    __GPR = "Добыча газа"

    __OIR = "Закачка нефти"
    __WIR = "Закачка воды"
    __GIR = "Закачка газа"

    __OVPR = "Добыча нефти (п.у.)"
    __WVPR = "Добыча воды (п.у.)"
    __GVPR = "Добыча газа (п.у.)"

    __OVIR = "Закачка нефти (п.у.)"
    __WVIR = "Закачка воды (п.у.)"
    __GVIR = "Закачка газа (п.у.)"

    __WCT = "Обводненность"
    __GOR = "Газовый фактор"
    __Comp = "Компенсация"
    __CumComp = "Накопленная Компенсация"

    __PI = "Индекс продуктивности"
    __PIO = "Индекс продуктивности по нефти"
    __PIW = "Индекс продуктивности по воде"
    __PIG = "Индекс продуктивности по газу"

    __ths = {
        "well_flag": True,
        "group_flag": True,
        "mylti": 10**3,
        "mylti_name": "тыс.",
    }

    __bil = {
        "well_flag": True,
        "group_flag": True,
        "mylti": 10**6,
        "mylti_name": "млн.",
    }

    def __init__(self, request: Iterable[Tuple[str, bool]] = None) -> None:

        self.OPT = CumWrite("OPT", self.__OPT, "м³", True, **self.__ths)
        self.WPT = CumWrite("WPT", self.__WPT, "м³", True, **self.__ths)
        self.GPT = CumWrite("GPT", self.__GPT, "м³", True, **self.__bil)
        # self.LPT = CumWrite("GPT", "Нак. газ", True, True, True)

        self.OIT = CumWrite("OIT", self.__OIT, "м³", False, **self.__ths)
        self.WIT = CumWrite("WIT", self.__WIT, "м³", True, **self.__ths)
        self.GIT = CumWrite("GIT", self.__GIT, "м³", True, **self.__bil)

        self.WTT = WTT("WTT", "Нак. время. работы", "Дни", True, True, False)
        self.WT = FPCWrite("WTT", "Время. работы", "Дни", True, True, False)

        self.OVPT = CumWrite("OVPT", self.__OVPT, "м³", False, **self.__ths)
        self.WVPT = CumWrite("WVPT", self.__WVPT, "м³", False, **self.__ths)
        self.GVPT = CumWrite("GVPT", self.__GVPT, "м³", False, **self.__ths)

        self.OVIT = CumWrite("OVIT", self.__OVPT, "м³", False, **self.__ths)
        self.WVIT = CumWrite("WVIT", self.__OVPT, "м³", False, **self.__ths)
        self.GVIT = CumWrite("GVIT", self.__OVPT, "м³", False, **self.__ths)

        self.BP9 = CumWrite("BP9", self.__BP9, "Бар", False, True, False)
        self.BHP = CumWrite("BHP", self.__BHP, "Бар", False, True, False)
        self.THP = CumWrite("THP", self.__THP, "Бар", False, True, False)

        self.OPR = FPCWrite("OPT", self.__OPR, "м³", True, **self.__ths)
        self.WPR = FPCWrite("WPT", self.__WPR, "м³", True, **self.__ths)
        self.GPR = FPCWrite("GPT", self.__GPR, "м³", True, **self.__bil)

        self.OIR = FPCWrite("OIT", self.__OIR, "м³", False, **self.__ths)
        self.WIR = FPCWrite("WIT", self.__WIR, "м³", True, **self.__ths)
        self.GIR = FPCWrite("GIT", self.__GIR, "м³", True, **self.__bil)

        self.OVPR = FPCWrite("OVPT", self.__OVPR, "м³", False, **self.__ths)
        self.WVPR = FPCWrite("WVPT", self.__WVPR, "м³", False, **self.__ths)
        self.GVPR = FPCWrite("GVPT", self.__GVPR, "м³", False, **self.__ths)

        self.OVIR = FPCWrite("OVIT", self.__OVIR, "м³", False, **self.__ths)
        self.WVIR = FPCWrite("WVIT", self.__WVIR, "м³", False, **self.__ths)
        self.GVIR = FPCWrite("GVIT", self.__GVIR, "м³", False, **self.__ths)

        self.WCT = WaterCut(self.__WCT, "Доли ед.", True, True, True)
        self.GOR = GOR(self.__GOR, "м³/м³", True, True, True)
        self.Comp = Compensation(self.__Comp, "Доли ед.", True, False, True)
        self.CumComp = CumComp(self.__CumComp, "Доли ед.", True, False, True)

        self.PI = CumWrite("PI", self.__PI, "м³/сут/бар", False, True, False)
        self.PIO = CumWrite("PIO", self.__PIO, "м³/сут/бар", False, True, False)
        self.PIW = CumWrite("PIW", self.__PIW, "м³/сут/бар", False, True, False)
        self.PIG = CumWrite("PIG", self.__PIG, "м³/сут/бар", False, True, False)

        self.AllField = (
            self.OPT,
            self.WPT,
            self.GPT,
            # self.LPT = CumWrite("GPT", "Нак. газ", True, True, True)
            self.OIT,
            self.WIT,
            self.GIT,
            self.WTT,
            self.WT,
            self.OVPT,
            self.WVPT,
            self.GVPT,
            self.OVIT,
            self.WVIT,
            self.GVIT,
            self.BP9,
            self.BHP,
            self.THP,
            self.OPR,
            self.WPR,
            self.GPR,
            self.OIR,
            self.WIR,
            self.GIR,
            self.OVPR,
            self.WVPR,
            self.GVPR,
            self.OVIR,
            self.WVIR,
            self.GVIR,
            self.WCT,
            self.GOR,
            self.Comp,
            self.CumComp,
            self.PI,
            self.PIO,
            self.PIW,
            self.PIG,
        )
        if request is not None:
            self.set_request(request)

    def set_request(self, request: Iterable[Tuple[str, bool]]) -> None:
        for name, what in request:
            atr = getattr(self, name)
            if isinstance(atr, KeywordReport):
                atr.Print = name

    @staticmethod
    def get_all_time(summary: List[SUMMARY]) -> TimeVector:
        tv = deepcopy(summary[0].TimeVector)
        for model in summary[1:]:
            tv.extend(model.TimeVector)

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

    def get_write_field(self) -> Iterable[KeywordReport]:
        for value in self.AllField:
            yield value


class CalcExcelReporter:

    formula = (
        "=VLOOKUP("
        "   INDEX($1:$1048576,ROW(),4),"
        "   Data!$1:$1048576,"
        "   1+SUMIFS("
        "       Data!$1:$1,"
        "       Data!$2:$2,"
        "       {ModelName},"
        "       Data!$3:$3,"
        "       {ObjectName},"
        "       Data!$4:$4,"
        "       {ParamName}"
        "       ),"
        "       False"
        ")"
    ).replace(" ", "")

    formula_unit = (
        "=INDEX("
        "   Data!$5:$5,"
        "   1+SUMIFS("
        "       Data!$1:$1,"
        "       Data!$2:$2,"
        "       {ModelName},"
        "       Data!$3:$3,"
        "       {ObjectName},"
        "       Data!$4:$4,"
        "       {ParamName}"
        "       )"
        ")"
    ).replace(" ", "")

    def __init__(self, step: str = "M", value_step: int = 1) -> None:
        self.Step = step
        self.StepValue = value_step
        pass

    @staticmethod
    def __write_time(
        sheet: xlsw.workbook.Worksheet,
        book: xlsw.workbook.Workbook,
        tv: TimeVector,
        row: int,
        col: int,
    ) -> None:
        time_format = book.add_format({"num_format": "yyyy-mm-dd"})
        for tid, tp in enumerate(tv.to_datetime_list()):
            sheet.write_datetime(row + tid, col, tp, time_format)

    def __get_tv(self, summary: List[SUMMARY]) -> TimeVector:
        tv = deepcopy(summary[0].TimeVector)
        for model in summary[1:]:
            tv.extend(model.TimeVector)

        add_tv = generate_time_vector(
            tv.min, tv.max, self.Step, self.StepValue, flat_borders=True
        )
        return add_tv

    def writhe(
        self,
        book: xlsw.Workbook,
        summary: Iterable[SUMMARY],
        tv: TimeVector,
        request: Request,
    ) -> None:
        sheet = book.add_worksheet("Data")
        self.__write_time(sheet, book, tv, 5, 0)
        nf = book.add_format({"num_format": "0.00"})
        i = 1
        for model in summary:
            for field in request.get_write_field():

                if field.WellFlag and field.Print:
                    for wname in model.get_well_names():
                        sheet.write(0, i, i)
                        sheet.write(1, i, model.CalcName)
                        sheet.write(2, i, wname)
                        sheet.write(3, i, field.Name)
                        sheet.write(4, i, field.get_unit())
                        value = field.get_well(wname, model, tv)
                        if value is not None:
                            sheet.write_column(5, i, value / field.Mylti, nf)
                        i += 1

                if field.GroupFlag and field.Print:
                    for gname in model.get_group_name():
                        sheet.write(0, i, i)
                        sheet.write(1, i, model.CalcName)
                        sheet.write(2, i, gname)
                        sheet.write(3, i, field.Name)
                        sheet.write(4, i, field.get_unit())
                        value = field.get_group(gname, model, tv)
                        if value is not None:
                            sheet.write_column(5, i, value / field.Mylti, nf)
                        i += 1

    @staticmethod
    def get_object_group(
        summary: Iterable[SUMMARY],
        request: Request,
    ) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        wname = []
        gname = []
        cname = []
        for model in summary:
            wname.extend(model.get_well_names())
            gname.extend(model.get_group_name())
            cname.append(model.CalcName)

        wpname = []
        gpname = []

        for filed in request.AllField:
            if filed.WellFlag and filed.Print:
                wpname.append(filed.Name)
            if filed.GroupFlag and filed.Print:
                gpname.append(filed.Name)

        wname = list(pd.unique(wname))
        gname = list(pd.unique(gname))
        cname = list(pd.unique(cname))
        wpname = list(pd.unique(wpname))
        gpname = list(pd.unique(gpname))

        wname.sort()
        gname.sort()
        cname.sort()
        wpname.sort()
        gpname.sort()

        return wname, gname, cname, wpname, gpname

    @staticmethod
    def writhe_technical_list(
        book: xlsw.Workbook,
        wells_name: List[str],
        group_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
        group_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("TechnicalList")
        sheet.write_column(0, 0, wells_name)
        sheet.write_column(0, 1, group_name)
        sheet.write_column(0, 2, calc_name)
        sheet.write_column(0, 3, well_param_name)
        sheet.write_column(0, 4, group_param_name)

    def universal_notation(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        data: Dict[str, str],
    ) -> None:
        sheet = book.add_worksheet(data["SheetName"])
        sheet.write(0, 0, data["ChooseName1"])
        sheet.write(1, 0, data["ChooseName2"])
        sheet.write(0, 1, data["ChooseBaseValue1"])
        sheet.write(1, 1, data["ChooseBaseValue2"])
        sheet.data_validation("B1", {"validate": "list", "source": data["CL1"]})
        sheet.data_validation("B2", {"validate": "list", "source": data["CL2"]})
        sheet.write_row(0, 4, data["ColumnName"])
        self.__write_time(sheet, book, tv, 2, 3)
        nf = book.add_format({"num_format": "0.00"})
        formula = self.formula.format(**data)
        formula_unit = self.formula_unit.format(**data)
        for col in range(len(data["ColumnName"])):
            sheet.write_formula(1, col + 4, formula_unit, nf)
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, formula, nf)


    def write_well(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        wells_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
    ) -> None:
        data = {
            "SheetName": "Wells",
            "ChooseName1": "Model",
            "ChooseName2": "Param",
            "ChooseBaseValue1": calc_name[0],
            "ChooseBaseValue2": well_param_name[0],
            "CL1": f"TechnicalList!C1:C{len(calc_name)}",
            "CL2": f"TechnicalList!D1:D{len(well_param_name)}",
            "ColumnName": wells_name,
            "ModelName": "$B$1",
            "ObjectName": "INDEX($1:$1,COLUMN())",
            "ParamName": "$B$2",
        }
        self.universal_notation(book, tv, data)

    def write_well_param(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        wells_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
    ) -> None:
        data = {
            "SheetName": "WellParam",
            "ChooseName1": "Model",
            "ChooseName2": "Well",
            "ChooseBaseValue1": calc_name[0],
            "ChooseBaseValue2": wells_name[0],
            "CL1": f"TechnicalList!C1:C{len(calc_name)}",
            "CL2": f"TechnicalList!A1:A{len(well_param_name)}",
            "ColumnName": well_param_name,
            "ModelName": "$B$1",
            "ObjectName": "$B$2",
            "ParamName": "INDEX($1:$1,COLUMN())",
        }
        self.universal_notation(book, tv, data)

    def write_well_model(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        wells_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
    ) -> None:
        data = {
            "SheetName": "WellModel",
            "ChooseName1": "Param",
            "ChooseName2": "Well",
            "ChooseBaseValue1": well_param_name[0],
            "ChooseBaseValue2": wells_name[0],
            "CL1": f"TechnicalList!D1:D{len(wells_name)}",
            "CL2": f"TechnicalList!A1:A{len(well_param_name)}",
            "ColumnName": calc_name,
            "ModelName": "INDEX($1:$1,COLUMN())",
            "ObjectName": "$B$2",
            "ParamName": "$B$1",
        }
        self.universal_notation(book, tv, data)

    def write_group(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        group_name: List[str],
        calc_name: List[str],
        group_param_name: List[str],
    ) -> None:
        data = {
            "SheetName": "Group",
            "ChooseName1": "Model",
            "ChooseName2": "Param",
            "ChooseBaseValue1": calc_name[0],
            "ChooseBaseValue2": group_param_name[0],
            "CL1": f"TechnicalList!C1:C{len(calc_name)}",
            "CL2": f"TechnicalList!E1:E{len(group_param_name)}",
            "ColumnName": group_name,
            "ModelName": "$B$1",
            "ObjectName": "INDEX($1:$1,COLUMN())",
            "ParamName": "$B$2",
        }
        self.universal_notation(book, tv, data)

    def write_group_param(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        group_name: List[str],
        calc_name: List[str],
        group_param_name: List[str],
    ) -> None:
        data = {
            "SheetName": "GroupParam",
            "ChooseName1": "Model",
            "ChooseName2": "Well",
            "ChooseBaseValue1": calc_name[0],
            "ChooseBaseValue2": group_name[0],
            "CL1": f"TechnicalList!C1:C{len(calc_name)}",
            "CL2": f"TechnicalList!B1:B{len(group_param_name)}",
            "ColumnName": group_param_name,
            "ModelName": "$B$1",
            "ObjectName": "$B$2",
            "ParamName": "INDEX($1:$1,COLUMN())",
        }
        self.universal_notation(book, tv, data)

    def write_group_model(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        group_name: List[str],
        calc_name: List[str],
        group_param_name: List[str],
    ) -> None:
        data = {
            "SheetName": "GroupModel",
            "ChooseName1": "Param",
            "ChooseName2": "Well",
            "ChooseBaseValue1": group_param_name[0],
            "ChooseBaseValue2": group_name[0],
            "CL1": f"TechnicalList!E1:E{len(group_name)}",
            "CL2": f"TechnicalList!B1:B{len(group_param_name)}",
            "ColumnName": calc_name,
            "ModelName": "INDEX($1:$1,COLUMN())",
            "ObjectName": "$B$2",
            "ParamName": "$B$1",
        }
        self.universal_notation(book, tv, data)

    def create(
        self,
        path: Union[Path, str],
        summary: Union[SUMMARY, Iterable[SUMMARY]],
        request: Request,
    ) -> None:
        if isinstance(summary, SUMMARY):
            summary = [summary]
        else:
            summary = list(summary)

        book = xlsw.Workbook(path)
        tv = self.__get_tv(summary)
        fun = self.get_object_group
        wname, gname, cname, wpname, gpname = fun(summary, request)
        self.writhe(book, summary, tv, request)
        self.writhe_technical_list(book, wname, gname, cname, wpname, gpname)
        self.write_well(book, tv, wname, cname, wpname)
        self.write_well_param(book, tv, wname, cname, wpname)
        self.write_well_model(book, tv, wname, cname, wpname)
        self.write_group(book, tv, gname, cname, gpname)
        self.write_group_param(book, tv, gname, cname, gpname)
        self.write_group_model(book, tv, gname, cname, gpname)
        book.close()


class ColumnarReportCreator:
    def __init__(
        self,
        start: Union[TimePoint, np.datetime64, str] = None,
        end: Union[TimePoint, np.datetime64, str] = None,
        step: str = "M",
        value_step: int = 1,
    ) -> None:
        self.Start = self.__init_time(start)
        self.End = self.__init_time(end)
        self.Step = step
        self.StepValue = value_step
        self.ModelBound = False

    @staticmethod
    def __init_time(
        time: Union[TimePoint, np.datetime64, str] = None,
    ) -> Optional[np.datetime64]:
        if isinstance(time, TimePoint):
            return time.to_datetime64()
        elif isinstance(time, str):
            return np.datetime64(time)
        elif isinstance(time, np.datetime64):
            return time
        elif time is None:
            return time
        else:
            raise TypeError

    def __get_tv(
        self,
        summary: List[SUMMARY],
    ) -> Tuple[TimeVector, TimeVector]:
        tv = deepcopy(summary[0].TimeVector)
        for model in summary[1:]:
            tv.extend(model.TimeVector)

        if self.Start is not None and not self.ModelBound:
            start = self.Start
        elif self.Start is not None:
            start = min([tv.min, self.Start])
        else:
            start = tv.min

        if self.End is not None and not self.ModelBound:
            end = self.End
        elif self.Start is not None:
            end = max([tv.max, self.End])
        else:
            end = tv.max

        add_tv = generate_time_vector(
            TimePoint(start),
            TimePoint(end),
            self.Step,
            self.StepValue,
            flat_borders=False,
        )

        start_tv = add_tv[:-1]
        end_tv = add_tv[1:]

        return start_tv, end_tv

    @staticmethod
    def get_object_group(
        summary: Iterable[SUMMARY],
        request: Request,
    ) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        wname = []
        gname = []
        cname = []
        for model in summary:
            wname.extend(model.get_well_names())
            gname.extend(model.get_group_name())
            cname.append(model.CalcName)

        wpname = []
        gpname = []

        for filed in request.AllField:
            if filed.WellFlag and filed.Print:
                wpname.append(filed.Name)
            if filed.GroupFlag and filed.Print:
                gpname.append(filed.Name)

        wname = list(pd.unique(wname))
        gname = list(pd.unique(gname))
        cname = list(pd.unique(cname))
        wpname = list(pd.unique(wpname))
        gpname = list(pd.unique(gpname))

        wname.sort()
        gname.sort()
        cname.sort()
        wpname.sort()
        gpname.sort()

        return wname, gname, cname, wpname, gpname

    @staticmethod
    def write_prod_list(
        book: xlsw.Workbook,
        request: Request,
        summary: List[SUMMARY],
        start_tv: TimeVector,
        end_tv: TimeVector,
        well_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("Prod")
        nf = book.add_format({"num_format": "0.00"})
        tf = book.add_format({"num_format": "yyyy-mm"})
        tfes = book.add_format({"num_format": "yyyy-mm-dd"})

        for_write = ["Период", "Начало", "Окончание", "Модель", "Скважина"]
        sheet.write_row(0, 0, for_write)

        jcol = 5
        for field in request.get_write_field():
            if field.WellFlag and field.Print:
                sheet.write(0, jcol, field.Name, nf)
                sheet.write(1, jcol, field.get_unit(), nf)
                jcol += 1

        irow = 2
        for model in summary:
            for wname in well_name:

                for tid, tp in enumerate(start_tv.to_datetime_list()):
                    sheet.write_datetime(irow + tid, 0, tp, tf)
                for tid, tp in enumerate(start_tv.to_datetime_list()):
                    sheet.write_datetime(irow + tid, 1, tp, tfes)
                for tid, tp in enumerate(end_tv.to_datetime_list()):
                    sheet.write_datetime(irow + tid, 2, tp, tfes)

                mname = model.CalcName
                sheet.write_column(irow, 3, [mname] * start_tv.shape())
                sheet.write_column(irow, 4, [wname] * start_tv.shape())

                jcol = 5
                for field in request.get_write_field():
                    if field.WellFlag and field.Print:
                        data = field.get_well(wname, model, start_tv)
                        multi = field.Mylti
                        sheet.write_column(irow, jcol, data / multi, nf)
                        jcol += 1

                irow += start_tv.shape()

    def create(
        self,
        path: Union[Path, str],
        summary: Union[SUMMARY, Iterable[SUMMARY]],
        request: Request,
    ) -> None:
        if isinstance(summary, SUMMARY):
            summary = [summary]
        else:
            summary = list(summary)

        book = xlsw.Workbook(path)
        start, end = self.__get_tv(summary)
        fun = self.get_object_group
        wname, gname, cname, wpname, gpname = fun(summary, request)
        self.write_prod_list(book, request, summary, start, end, wname)
        book.close()
