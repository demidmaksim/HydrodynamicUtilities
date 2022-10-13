from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from typing import Union, List, Tuple, Optional

from typing import Iterable

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


class CumWrite(KeywordReport):
    def __init__(
        self,
        mnemonic: str,
        name: str,
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Mnemonc = mnemonic
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
        to_report: bool = False,
        well_flag: bool = True,
        group_flag: bool = True,
    ) -> None:
        self.Name = name
        self.Print = to_report
        self.WellFlag = well_flag
        self.GroupFlag = group_flag

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
    def __init__(self, request: Iterable[Tuple[str, bool]] = None) -> None:

        self.OPT = CumWrite("OPT", "Нак. нефть", True, True, True)
        self.WPT = CumWrite("WPT", "Нак. воды", True, True, True)
        self.GPT = CumWrite("GPT", "Нак. газ", True, True, True)
        # self.LPT = CumWrite("GPT", "Нак. газ", True, True, True)

        self.OIT = CumWrite("OPT", "Нак. зак. нефть", True, True, True)
        self.WIT = CumWrite("WPT", "Нак. зак. воды", True, True, True)
        self.GIT = CumWrite("GPT", "Нак. зак. газ", True, True, True)

        self.WTT = WTT("WTT", "Нак. время. работы", True, True, False)

        self.OVPT = CumWrite("OVPT", "Нак. нефть (пл. усл.)", False, True, True)
        self.WVPT = CumWrite("WVPT", "Нак. воды (пл. усл.)", False, True, True)
        self.GVPT = CumWrite("GVPT", "Нак. газ (пл. усл.)", False, True, True)

        self.OVIT = CumWrite("OVIT", "Нак. зак. нефти (п.у.)", False, True, True)
        self.WVIT = CumWrite("WVIT", "Нак. зак. воды (п.у.)", False, True, True)
        self.GVIT = CumWrite("GVIT", "Нак. зак. газа (п.у.)", False, True, True)

        self.BHP = CumWrite("BHP", "Забойное давление", False, True, False)
        self.THP = CumWrite("THP", "Забойное давление", False, True, False)

        self.OPR = FPCWrite("OPT", "Добыча нефти", True, True, True)
        self.WPR = FPCWrite("WPT", "Добыча воды", True, True, True)
        self.GPR = FPCWrite("GPT", "Добыча газа", True, True, True)

        self.OIR = FPCWrite("OIT", "Закачка нефти", False, True, True)
        self.WIR = FPCWrite("WIT", "Закачка воды", True, True, True)
        self.GIR = FPCWrite("GIT", "Закачка газа", True, True, True)

        self.OVPR = FPCWrite("OVPT", "Добыча нефти (п.у.)", False, True, True)
        self.WVPR = FPCWrite("WVPT", "Добыча воды (п.у.)", False, True, True)
        self.GVPR = FPCWrite("GVPT", "Добыча газа (п.у.)", False, True, True)

        self.OVIR = FPCWrite("OVIT", "Закачка нефти (п.у.)", False, True, True)
        self.WVIR = FPCWrite("WVIT", "Закачка воды (п.у.)", False, True, True)
        self.GVIR = FPCWrite("GVIT", "Закачка газа (п.у.)", False, True, True)

        self.WCT = WaterCut("Обводненность", True, True, True)
        self.GOR = GOR("Газовый фактор", True, True, True)
        self.Comp = Compensation("Компенсация", True, True, True)
        self.CumComp = CumCompensation("Накопленная Компенсация", True, True, True)

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
    def __int__(self) -> None:
        pass

    def __write_time(
        self,
        sheet: xlsw.workbook.Worksheet,
        book: xlsw.workbook.Workbook,
        tv: TimeVector,
        row: int,
        col: int,
    ) -> None:
        time_format = book.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})
        for tid, tp in enumerate(tv.to_datetime_list()):
            sheet.write_datetime(row + tid, col, tp, time_format)

    def __get_tv(self, summary: List[SUMMARY]) -> TimeVector:
        tv = deepcopy(summary[0].TimeVector)
        for model in summary[1:]:
            tv.extend(model.TimeVector)

        add_tv = generate_time_vector(tv.min, tv.max, "M", value_step=1)
        return add_tv

    def writhe(
        self,
        book: xlsw.Workbook,
        summary: Iterable[SUMMARY],
        tv: TimeVector,
        request: Request,
    ) -> None:
        sheet = book.add_worksheet("Data")
        self.__write_time(sheet, book, tv, 4, 0)
        i = 1
        for model in summary:
            for field in request.get_write_field():

                if field.WellFlag and field.Print:
                    for wname in model.get_well_names():
                        sheet.write(0, i, i)
                        sheet.write(1, i, model.CalcName)
                        sheet.write(2, i, wname)
                        sheet.write(3, i, field.Name)
                        value = field.get_well(wname, model, tv)
                        if value is not None:
                            sheet.write_column(4, i, value)
                        i += 1

                if field.GroupFlag and field.Print:
                    for gname in model.get_group_name():
                        sheet.write(0, i, i)
                        sheet.write(1, i, model.CalcName)
                        sheet.write(2, i, gname)
                        sheet.write(3, i, field.Name)
                        value = field.get_group(gname, model, tv)
                        if value is not None:
                            sheet.write_column(4, i, value)
                        i += 1

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
        self.writhe(book, summary, tv, request)
        book.close()
