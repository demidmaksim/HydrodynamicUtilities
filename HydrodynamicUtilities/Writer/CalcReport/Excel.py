from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Tuple, Optional

from typing import Iterable

import numpy as np
import pandas as pd

import xlsxwriter as xlsw
from pathlib import Path
from HydrodynamicUtilities.Models.EclipseBinaryFile import SUMMARY
from HydrodynamicUtilities.Models.ParamVector import CumTimeSeriasParam, TimeSeries
from HydrodynamicUtilities.Models.Time import TimeVector, generate_time_vector

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
                periods = tv.get_periods()
                op = summary.get(f"WOPT", name).to_cum_time_series()
                wp = summary.get(f"WOPT", name).to_cum_time_series()
                gp = summary.get(f"WOPT", name).to_cum_time_series()

                dop = op.get_delta_serias()
                dwp = wp.get_delta_serias()
                dgp = gp.get_delta_serias()

                oi = summary.get(f"WOIT", name).to_cum_time_series()
                wi = summary.get(f"WOIT", name).to_cum_time_series()
                gi = summary.get(f"WOIT", name).to_cum_time_series()

                doi = oi.get_delta_serias()
                dwi = wi.get_delta_serias()
                dgi = gi.get_delta_serias()

                rate_from_cum = dop + dwp + dgp + doi + dwi + dgi

                op = summary.get(f"WOPR", name).to_rate_time_series()
                wp = summary.get(f"WOPR", name).to_rate_time_series()
                gp = summary.get(f"WOPR", name).to_rate_time_series()
                oi = summary.get(f"WOIR", name).to_rate_time_series()
                wi = summary.get(f"WOIR", name).to_rate_time_series()
                gi = summary.get(f"WOIR", name).to_rate_time_series()

                rate = op + wp + gp + oi + wi + gi

                rate_from_cum[rate_from_cum.values == 0] = 0
                rate[rate.values == 0] = 1

                wefac = rate_from_cum / rate
                wefac = wefac.retime(tv)
                return periods * wefac.values
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
        value = ts.retime(tv)
        results = value.get_delta_serias()
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


class CumCompensation(KeywordReport):
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

    __BHP = "Забойное давление"
    __THP = "Забойное давление"

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

    __ths = {
        "well_flag": True,
        "group_flag": True,
        "mylti": 10 ** 3,
        "mylti_name": "тыс.",
    }

    __bil = {
        "well_flag": True,
        "group_flag": True,
        "mylti": 10 ** 6,
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

        self.OVPT = CumWrite("OVPT", self.__OVPT, "м³", False, **self.__ths)
        self.WVPT = CumWrite("WVPT", self.__WVPT, "м³", False, **self.__ths)
        self.GVPT = CumWrite("GVPT", self.__GVPT, "м³", False, **self.__ths)

        self.OVIT = CumWrite("OVIT", self.__OVPT, "м³", False, **self.__ths)
        self.WVIT = CumWrite("WVIT", self.__OVPT, "м³", False, **self.__ths)
        self.GVIT = CumWrite("GVIT", self.__OVPT, "м³", False, **self.__ths)

        self.BHP = CumWrite("BHP", self.__BHP, "Бар", False, True, False)
        self.THP = CumWrite("THP", self.__BHP, "Бар", False, True, False)

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
        self.CumComp = CumCompensation(self.__CumComp, "Доли ед.", True, False, True)

        self.AllField = (
            self.OPT,
            self.WPT,
            self.GPT,
            # self.LPT = CumWrite("GPT", "Нак. газ", True, True, True)
            self.OIT,
            self.WIT,
            self.GIT,
            self.WTT,
            self.OVPT,
            self.WVPT,
            self.GVPT,
            self.OVIT,
            self.WVIT,
            self.GVIT,
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

    def get_write_field(self) -> Iterable[KeywordReport]:
        for value in self.AllField:
            yield value


class CalcExcelReporter:
    formula_by_object = (
        "=VLOOKUP("
        "   INDEX($1:$1048576,ROW(),4),"
        "   Data!$1:$1048576,"
        "   1+SUMIFS("
        "       Data!$1:$1,"
        "       Data!$2:$2,"
        "       $B$1,"
        "       Data!$3:$3,"
        "       INDEX($1:$1,COLUMN()),"
        "       Data!$4:$4,"
        "       $B$2"
        "       ),"
        "       False"
        ")"
    ).replace(" ", "")

    formula_by_param = (
        "=VLOOKUP("
        "   INDEX($1:$1048576,ROW(),4),"
        "   Data!$1:$1048576,"
        "   1+SUMIFS("
        "       Data!$1:$1,"
        "       Data!$2:$2,"
        "       $B$1,"
        "       Data!$3:$3,"
        "       $B$2,"
        "       Data!$4:$4,"
        "       INDEX($1:$1,COLUMN())"
        "       ),"
        "       False"
        ")"
    ).replace(" ", "")

    formula_by_model = (
        "=VLOOKUP("
        "   INDEX($1:$1048576,ROW(),4),"
        "   Data!$1:$1048576,"
        "   1+SUMIFS("
        "       Data!$1:$1,"
        "       Data!$2:$2,"
        "       INDEX($1:$1,COLUMN()),"
        "       Data!$3:$3,"
        "       $B$2,"
        "       Data!$4:$4,"
        "       $B$1"
        "       ),"
        "       False"
        ")"
    ).replace(" ", "")

    def __init__(self, step: str = "Y", value_step: int = 1) -> None:
        self.Step = step
        self.StepValue = value_step
        pass

    def __write_time(
        self,
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

    def get_object_group(
        self,
        summary: Iterable[SUMMARY],
        request: Request,
    ) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        wells_name = []
        group_name = []
        calc_name = []
        for model in summary:
            wells_name.extend(model.get_well_names())
            group_name.extend(model.get_group_name())
            calc_name.append(model.CalcName)

        well_param_name = []
        group_param_name = []

        for filed in request.AllField:
            if filed.WellFlag and filed.Print:
                well_param_name.append(filed.Name)
            if filed.GroupFlag and filed.Print:
                group_param_name.append(filed.Name)

        wells_name = list(pd.unique(wells_name))
        group_name = list(pd.unique(group_name))
        calc_name = list(pd.unique(calc_name))
        well_param_name = list(pd.unique(well_param_name))
        group_param_name = list(pd.unique(group_param_name))

        wells_name.sort()
        group_name.sort()
        calc_name.sort()
        well_param_name.sort()
        group_param_name.sort()

        return wells_name, group_name, calc_name, well_param_name, group_param_name

    def writhe_technical_list(
        self,
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

    def write_well(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        wells_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("Wells")
        sheet.write(0, 0, "Model")
        sheet.write(1, 0, "Param")
        sheet.write(0, 1, calc_name[0])
        sheet.write(1, 1, well_param_name[0])
        sheet.data_validation(
            "B2",
            {
                "validate": "list",
                "source": f"TechnicalList!D1:D{len(well_param_name)}",
            },
        )
        sheet.data_validation(
            "B1",
            {
                "validate": "list",
                "source": f"TechnicalList!C1:C{len(calc_name)}",
            },
        )
        sheet.write_row(0, 4, wells_name)
        self.__write_time(sheet, book, tv, 2, 3)

        nf = book.add_format({"num_format": "0.00"})

        for col in range(len(wells_name)):
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, self.formula_by_object, nf)

    def write_group(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        group_name: List[str],
        calc_name: List[str],
        group_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("Group")
        sheet.write(0, 0, "Model")
        sheet.write(1, 0, "Param")
        sheet.write(0, 1, calc_name[0])
        sheet.write(1, 1, group_param_name[0])
        sheet.data_validation(
            "B2",
            {
                "validate": "list",
                "source": f"TechnicalList!E1:E{len(group_param_name)}",
            },
        )
        sheet.data_validation(
            "B1",
            {
                "validate": "list",
                "source": f"TechnicalList!C1:C{len(calc_name)}",
            },
        )
        sheet.write_row(0, 4, group_name)
        self.__write_time(sheet, book, tv, 2, 3)

        nf = book.add_format({"num_format": "0.00"})

        for col in range(len(group_name)):
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, self.formula_by_object, nf)

    def write_well_param(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        well_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("WellParam")
        sheet.write(0, 0, "Model")
        sheet.write(1, 0, "Well")
        sheet.write(0, 1, calc_name[0])
        sheet.write(1, 1, well_name[0])
        sheet.data_validation(
            "B2",
            {
                "validate": "list",
                "source": f"TechnicalList!A1:A{len(well_param_name)}",
            },
        )
        sheet.data_validation(
            "B1",
            {
                "validate": "list",
                "source": f"TechnicalList!C1:C{len(calc_name)}",
            },
        )
        sheet.write_row(0, 4, well_param_name)
        self.__write_time(sheet, book, tv, 2, 3)

        nf = book.add_format({"num_format": "0.00"})

        for col in range(len(well_param_name)):
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, self.formula_by_param, nf)

    def write_group_param(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        group_name: List[str],
        calc_name: List[str],
        group_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("GroupParam")
        sheet.write(0, 0, "Model")
        sheet.write(1, 0, "Group")
        sheet.write(0, 1, calc_name[0])
        sheet.write(1, 1, group_name[0])
        sheet.data_validation(
            "B2",
            {
                "validate": "list",
                "source": f"TechnicalList!B1:B{len(group_name)}",
            },
        )
        sheet.data_validation(
            "B1",
            {
                "validate": "list",
                "source": f"TechnicalList!C1:C{len(calc_name)}",
            },
        )
        sheet.write_row(0, 4, group_param_name)
        self.__write_time(sheet, book, tv, 2, 3)

        nf = book.add_format({"num_format": "0.00"})

        for col in range(len(group_param_name)):
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, self.formula_by_param, nf)

    def write_well_model(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        well_name: List[str],
        calc_name: List[str],
        well_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("WellModel")
        sheet.write(0, 0, "Param")
        sheet.write(1, 0, "Well")
        sheet.write(0, 1, well_param_name[0])
        sheet.write(1, 1, well_name[0])
        sheet.data_validation(
            "B2",
            {
                "validate": "list",
                "source": f"TechnicalList!A1:A{len(well_param_name)}",
            },
        )
        sheet.data_validation(
            "B1",
            {
                "validate": "list",
                "source": f"TechnicalList!D1:D{len(well_param_name)}",
            },
        )
        sheet.write_row(0, 4, calc_name)
        self.__write_time(sheet, book, tv, 2, 3)

        nf = book.add_format({"num_format": "0.00"})

        for col in range(len(calc_name)):
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, self.formula_by_model, nf)

    def write_group_model(
        self,
        book: xlsw.Workbook,
        tv: TimeVector,
        group_name: List[str],
        calc_name: List[str],
        group_param_name: List[str],
    ) -> None:
        sheet = book.add_worksheet("GroupModel")
        sheet.write(0, 0, "Param")
        sheet.write(1, 0, "Group")
        sheet.write(0, 1, group_param_name[0])
        sheet.write(1, 1, group_name[0])
        sheet.data_validation(
            "B2",
            {
                "validate": "list",
                "source": f"TechnicalList!B1:B{len(group_name)}",
            },
        )
        sheet.data_validation(
            "B1",
            {
                "validate": "list",
                "source": f"TechnicalList!E1:E{len(group_param_name)}",
            },
        )
        sheet.write_row(0, 4, calc_name)
        self.__write_time(sheet, book, tv, 2, 3)

        nf = book.add_format({"num_format": "0.00"})

        for col in range(len(calc_name)):
            for row in range(len(tv.to_datetime64())):
                sheet.write_formula(row + 2, col + 4, self.formula_by_model, nf)

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
        wname, gname, cname, wpname, gpname = self.get_object_group(summary, request)
        self.writhe(book, summary, tv, request)
        self.writhe_technical_list(book, wname, gname, cname, wpname, gpname)
        self.write_well(book, tv, wname, cname, wpname)
        self.write_well_param(book, tv, wname, cname, wpname)
        self.write_well_model(book, tv, wname, cname, wpname)
        self.write_group(book, tv, gname, cname, gpname)
        self.write_group_param(book, tv, gname, cname, gpname)
        self.write_group_model(book, tv, gname, cname, gpname)
        book.close()
