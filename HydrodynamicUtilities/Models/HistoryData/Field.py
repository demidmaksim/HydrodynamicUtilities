from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Union, Iterable, Any
    from pathlib import Path

from .Well import WellHistory, WellControlMode, StopEventSetting
from HydrodynamicUtilities.Models.Time import TimePoint, TimeVector, NonLinearTime
from HydrodynamicUtilities.Models.Strategy import (
    ScheduleDataframe,
    Strategy,
    ReportSteps,
)

# from HydrodynamicUtilities.Writer import create_schedule, write_xlsx
import time
from multiprocessing import Pool


class FieldStepReport(NonLinearTime):
    def __init__(
        self,
        start: TimePoint,
        finish: TimePoint,
        base_step: Tuple[str, int],
        additional_control: Dict[TimePoint, Tuple[str, int]] = None,
    ) -> None:
        super().__init__(start, finish, base_step, additional_control)


class FieldHistory:
    __Base_Base_steps = ("D", 1)
    __Base_Start = TimePoint("2020-01-01")
    __Base_End = TimePoint("2021-01-01")

    def __init__(
        self,
        data: Union[List[WellHistory], Dict[str, WellHistory]] = None,
        fsr: FieldStepReport = None,
        additional_events: ScheduleDataframe = None,
        name: str = None,
    ) -> None:
        self.WellData: Dict[str, WellHistory] = dict()
        if isinstance(data, list):
            self.extend(data)
        elif isinstance(data, dict):
            self.extend(data.values())
        else:
            pass

        self.FSR = fsr
        self.AddEvents = additional_events
        self.FieldName = name

    def __repr__(self) -> str:
        if self.FieldName is None:
            return f"FieldHistory"
        else:
            return f"FieldHistory {self.FieldName}"

    def __getitem__(self, item: str) -> WellHistory:
        return self.WellData[item.upper()]

    def append(self, wh: WellHistory) -> None:
        self.WellData[wh.WellName.upper()] = wh

    def extend(self, wh_list: Iterable[WellHistory]) -> None:
        for wh in wh_list:
            self.append(wh)

    def __get_base_fsr(self) -> FieldStepReport:

        time_max = None
        time_min = None
        for whd in self.WellData:
            new_min, new_max = whd.get_time_limit()

            if time_min is None or new_min < time_min:
                time_min = new_min

            if time_max is None or time_max > new_max:
                time_max = new_max

        if time_min is None:
            time_min = self.__Base_Start

        if time_max is None:
            time_max = self.__Base_End

        return FieldStepReport(
            start=time_min,
            finish=time_max,
            base_step=self.__Base_Base_steps,
        )

    def set_steps_settings(
        self,
        start: Union[TimePoint, str],
        end: Union[TimePoint, str],
        base_step: Tuple[str, int],
        additional_control: Dict[Union[TimePoint, str], Tuple[str, int]] = None,
    ) -> None:
        if isinstance(start, str):
            start = TimePoint(start)
        if isinstance(end, str):
            end = TimePoint(end)

        if additional_control is not None:
            for key in list(additional_control.keys()):
                if isinstance(key, str):
                    tp = TimePoint(key)
                    additional_control[tp] = additional_control.pop(key)

        self.FSR = FieldStepReport(start, end, base_step, additional_control)

    def set_well_wefac_settings(self, wefac_flag: bool) -> None:
        for well in self.WellData.values():
            well.WEFAC = wefac_flag

    def set_well_prod_mode_settings(self, mode: str) -> None:
        for well in self.WellData.values():
            well.ProdMode = WellControlMode(mode)

    def set_well_inj_mode_settings(self, mode: str) -> None:
        for well in self.WellData.values():
            well.InjMode = WellControlMode(mode)

    def set_well_prod_event_settings(self, event_flag: bool) -> None:
        for well in self.WellData.values():
            well.ProdEvent = StopEventSetting(event_flag)

    def set_well_inj_event_settings(self, event_flag: bool) -> None:
        for well in self.WellData.values():
            well.InjEvent = StopEventSetting(event_flag)

    def get_cipher(self) -> str:
        if self.FSR is None:
            fsr = self.__get_base_fsr()
        else:
            fsr = self.FSR
        start = fsr.Start.to_datetime64().astype("datetime64[D]")
        end = fsr.Finish.to_datetime64().astype("datetime64[D]")
        base_t, base_n = fsr.BaseStep

        base_results = f"History_from_{start}_to_{end}_{base_n}{base_t}"

        if len(self.WellData.values()) == 1:
            keys = list(self.WellData.keys())
            return f"{base_results}_{keys[0]}"
        else:
            return base_results

    def get_time_vector(self) -> TimeVector:
        if self.FSR is None:
            fsr = self.__get_base_fsr().get_time_vector()
        else:
            fsr = self.FSR.get_time_vector()

        for well in self.WellData.values():
            t = well.get_events()
            t = t[(t > fsr.min) & (t < fsr.max)]
            fsr.extend(t)

        fsr.unique(in_place=True)
        fsr.sort(in_place=True)
        return fsr

    @staticmethod
    def _create_sch_for_multi(kwargs: Dict[str, Any]) -> ScheduleDataframe:
        well = kwargs["well"]
        tv = kwargs["tv"]
        return well.get_schedule(tv)

    def __get_multi_schedule(self, tv: TimeVector) -> ScheduleDataframe:
        iter_list = []
        for well in self.WellData.values():
            iter_list.append({"well": well, "tv": tv})

        with Pool(len(self.WellData.values())) as p:
            wells_sdf = list(p.map(self._create_sch_for_multi, iter_list))

        results = ScheduleDataframe()
        for well in wells_sdf:
            results = results + well

        return results

    def __get_schedule(self, tv: TimeVector) -> ScheduleDataframe:
        sdf = ScheduleDataframe()
        for well in self.WellData.values():
            t = time.time()
            sdf = sdf + well.get_schedule(tv)
            print(f"\tsdf: {round(time.time() - t, 2)}")
        return sdf

    def get_schedule(
        self,
        multiprocessing: bool = False,
    ) -> ScheduleDataframe:
        tv = self.get_time_vector()
        if multiprocessing:
            return self.__get_multi_schedule(tv)
        else:
            return self.__get_schedule(tv)

    def get_all_events(
        self,
        multiprocessing: bool = False,
    ) -> ScheduleDataframe:
        sdf = self.get_schedule(multiprocessing)
        sdf = sdf + self.AddEvents
        return sdf

    def convert_to_strategy(self, steps: ReportSteps = None) -> Strategy:
        sdf = self.get_all_events()
        return Strategy(sdf, steps)

    """
    def create_schedule(
        self,
        path: Union[str, Path] = "Results.sch",
        multiprocessing: bool = False,
    ) -> None:
        sdf = self.get_all_events(multiprocessing)
        tv = self.get_time_vector()
        create_schedule(sdf, tv, path)

    def to_excel(self, path: Union[str, Path] = "Results.xlsx") -> None:
        sdf = self.get_all_events()
        write_xlsx(sdf, path)
    """
