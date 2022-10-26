from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Tuple, List, Optional
    from pathlib import Path

import numpy as np
import pandas as pd

from copy import deepcopy

from ..Time import TimeVector, TimePoint, generate_time_vector
from HydrodynamicUtilities.Models.Strategy.Frame import ScheduleSheet, ScheduleDataframe
from ..Source import EclipseScheduleNames
from ..ParamVector import (
    StringInterpolationModel,
    StatusVector,
    InterpolationModel,
    TimeSeries,
)
from HydrodynamicUtilities.Painter.HistoryData import HistoryDataPainter
import time


class WellMeasurement:
    WhiteList = (
        "THP",
        "BHP",
        "OilProd",
        "WatProd",
        "GasProd",
        "OilInj",
        "WatInj",
        "GasInj",
        "Status",  # TODO rework Status to WEFAC?
    )

    ProdList = (
        WhiteList[2],
        WhiteList[3],
        WhiteList[4],
    )
    INJList = (
        WhiteList[5],
        WhiteList[6],
        WhiteList[7],
    )

    def __init__(self, time: TimeVector, data: np.ndarray = None):
        if data is None:
            self.DataFrame = pd.DataFrame(
                data=data,
                index=time.to_frame_index(),
            )
        else:
            self.DataFrame = pd.DataFrame(
                data=data,
                index=time.to_frame_index(),
                columns=self.WhiteList[: data.shape[1]],
            )

    def __setattr__(
        self, key: str, value: Union[np.ndarray, pd.Series, TimeSeries]
    ) -> None:
        if key not in self.WhiteList + ("DataFrame",):
            raise AttributeError

        if key == "DataFrame":
            return super().__setattr__(key, value)

        if type(value) == np.ndarray:
            self.DataFrame[key] = value
        elif type(value) == pd.Series:
            self.DataFrame[key] = value.values
        elif type(value) == TimeSeries:
            self.DataFrame[key] = value.Data
        else:
            raise TypeError()

    def __getattr__(self, key: str) -> TimeSeries:
        if key not in self.WhiteList + ("DataFrame",):
            raise AttributeError

        if key == "DataFrame":
            return super().__getattribute__(key)

        tv = self.get_time()
        values = self.DataFrame[key].values
        return TimeSeries(tv, values)

    def get_interpolation_model(self, key: str) -> InterpolationModel:
        if key not in self.WhiteList:
            raise AttributeError

        data = self.__getattr__(key)
        drop_data = data.drop_nan()
        if drop_data is None:
            data.Data = data.Data.fillna(0)
        else:
            data = drop_data

        if key != "Status":
            return InterpolationModel(data)
        else:
            return InterpolationModel(data, kind="zero")

    def get_time(self) -> TimeVector:
        return TimeVector(self.DataFrame.index.to_numpy())

    def get_time_limits(self) -> Tuple[TimePoint, TimePoint]:
        tv = self.get_time()
        return tv.min, tv.max

    def get_status(self) -> StatusVector:
        oil = ~pd.isna(self.OilProd.values)
        wat = ~pd.isna(self.WatProd.values)
        gas = ~pd.isna(self.GasProd.values)
        prod = oil | wat | gas

        oil = self.OilProd.values != 0
        wat = self.WatProd.values != 0
        gas = self.GasProd.values != 0
        not_zeros_prod = oil | wat | gas

        prod = prod & not_zeros_prod

        oil = ~pd.isna(self.OilInj.values)
        wat = ~pd.isna(self.WatInj.values)
        gas = ~pd.isna(self.GasInj.values)
        inj = oil | wat | gas

        oil = self.OilInj.values != 0
        wat = self.WatInj.values != 0
        gas = self.GasInj.values != 0
        not_zeros_inj = oil | wat | gas

        inj = inj & not_zeros_inj

        change = np.zeros(self.Status.shape())
        change[1:] = self.Status.values[1:] != self.Status.values[:-1]

        start = (change * self.Status.values).astype(bool)
        stop = (change * abs(1 - self.Status.values)).astype(bool)

        before_stopping = np.zeros(self.Status.shape())
        before_stopping[:-1] = stop[1:]
        before_stopping = before_stopping.astype(bool)

        before_start = np.zeros(self.Status.shape())
        before_start[:-1] = start[1:]
        before_start = before_start.astype(bool)

        mode = np.zeros(self.Status.shape()) * np.NAN
        mode[prod] = 1
        mode[inj] = -1

        mode_back = pd.Series(mode).fillna(method="bfill")
        mode_back = mode_back.fillna(method="ffill").values

        mode_forward = pd.Series(mode).fillna(method="ffill")
        mode_forward = mode_forward.fillna(method="bfill").values

        mode[before_stopping] = mode_forward[before_stopping]
        mode[start] = mode_back[start]

        mode[before_start] = 0
        mode[stop] = 0

        df = pd.Series(mode)
        df = df.fillna(method="ffill")
        df = df.fillna(method="bfill")

        mode = df.values * self.Status.values
        time = self.get_time()

        return StatusVector(time, mode)

    def to_excel(self, path: Path) -> None:
        df = deepcopy(self.DataFrame)
        df["status"] = self.get_status().values
        df["downtime_flag"] = self.get_status().get_downtime_flag().values
        df["work_flag"] = self.get_status().get_work_flag().values
        df["prod_mode_flag"] = self.get_status().get_prod_mode_flag().values
        df["inj_mode_flag"] = self.get_status().get_inj_mode_flag().values
        df["mode_change_flag"] = self.get_status().get_mode_change_flag().values
        df["start_flag"] = self.get_status().get_start_flag().values
        df["stop_flag"] = self.get_status().get_stop_flag().values
        df["work_time"] = self.get_status().get_work_time().values
        df["last_mode"] = self.get_status().get_last_mode().values
        # df["get_event_time"] = self.get_status().get_event_time()

        df.to_excel(path)


class ValesController(list):
    pass

    def append(self, __object) -> None:
        super(ValesController, self).append(__object)


class VFPHistory:
    def __init__(self, data: TimeSeries) -> None:
        self.__Data = data

    def get_value(self, tv: TimeVector) -> TimeSeries:
        data = self.__Data.drop_nan()

        if data is None:
            return TimeSeries(tv, np.zeros(tv.shape()) * np.NAN)

        model = InterpolationModel(data)
        value = model.get_value(tv)
        return value

    def get_new_vfp_time_moments(self) -> Optional[TimeVector]:
        return self.__Data.change_times()


class ConstructionHistory:
    def __init__(
        self,
        vfp: VFPHistory = None,
        valves: List[TimeSeries] = None,
    ) -> None:
        self.VFP = vfp
        self.Valves = valves


class CumWellData(WellMeasurement):
    def get_status(self) -> StatusVector:
        oil = self.OilProd.values[1:] - self.OilProd.values[:-1]
        wat = self.WatProd.values[1:] - self.WatProd.values[:-1]
        gas = self.GasProd.values[1:] - self.GasProd.values[:-1]
        prod = (oil + wat + gas) != 0
        prod = np.concatenate((prod, [False]))

        oil = self.OilInj.values[1:] - self.OilInj.values[:-1]
        wat = self.WatInj.values[1:] - self.WatInj.values[:-1]
        gas = self.GasInj.values[1:] - self.GasInj.values[:-1]
        inj = (oil + wat + gas) != 0
        inj = np.concatenate((inj, [False]))

        results = np.zeros(self.OilProd.shape())
        results[inj] = -1
        results[prod] = 1
        results[-1] = results[-2]

        return StatusVector(self.get_time(), results)


class WellControlMode(StringInterpolationModel):
    __ProdWhiteList = (
        "LRAT",
        "ORAT",
        "WRAT",
        "GRAT",
        "WGRA",
        "NGL",
        "RESV",
        "BHP",
        "THP",
        "TGRUP",
        "NONE",
    )

    __InjWhiteList = (
        "RATE",
        "BHP",
        "THP",
    )


class StopEventSetting(StringInterpolationModel):
    def get_value(self, tv: TimeVector) -> TimeSeries:
        ts = super().get_value(tv)
        return ts[ts.values]


class WEFACRecord(StringInterpolationModel):
    pass


def __fill_back(df: pd.DataFrame) -> pd.DataFrame:
    df = deepcopy(df)
    df = df.fillna(method="bfill")
    df = df.fillna(method="ffill")
    return df


def __fill_forward(df: pd.DataFrame) -> pd.DataFrame:
    df = deepcopy(df)
    df = df.fillna(method="ffill")
    df = df.fillna(method="bfill")
    return df


def __fill_change_mode_history(data: WellMeasurement) -> WellMeasurement:
    df_fill_back = __fill_back(data.DataFrame)
    df_fill_forward = __fill_forward(data.DataFrame)
    status = data.get_status()

    new = deepcopy(data)

    change_flag = status.get_mode_change_flag()
    stop_flag = status.get_stop_flag()
    start_flag = status.get_start_flag()

    new.DataFrame.loc[change_flag.values] = df_fill_forward[change_flag.values]
    new.DataFrame.loc[stop_flag.values] = df_fill_forward[stop_flag.values]
    new.DataFrame.loc[start_flag.values] = df_fill_back[start_flag.values]

    new.DataFrame.iloc[0] = df_fill_forward.iloc[0]
    new.DataFrame.iloc[-1] = df_fill_forward.iloc[-1]

    return new


def filing_rates(data: WellMeasurement) -> WellMeasurement:
    changed = __fill_change_mode_history(data)
    time = data.get_time()
    for param in changed.WhiteList:
        value = changed.get_interpolation_model(param).get_value(time)

        prod_mode = data.get_status().get_prod_mode_flag()
        inje_mode = data.get_status().get_inj_mode_flag()
        work_mode = data.get_status().get_work_flag()

        if param in changed.ProdList:
            value = value * prod_mode
            value = value * work_mode
        elif param in changed.INJList:
            value = value * inje_mode
            value = value * work_mode
        setattr(changed, param, value)

    return changed


def operation(
    prod_oil: TimeSeries,
    prod_wat: TimeSeries,
    prod_gas: TimeSeries,
) -> TimeSeries:
    pattern = (prod_oil + prod_wat + prod_gas) != 0
    results = np.zeros(prod_oil.shape()).astype(str)
    results[:] = "STOP"
    results[pattern] = "OPEN"
    return TimeSeries(prod_oil.get_time(), results)


def rates(
    data: CumWellData,
    time: TimeVector,
    mode: str = "Prod",
    wefac: TimeSeries = None,
) -> Tuple[TimeSeries, TimeSeries, TimeSeries]:
    oil = data.get_interpolation_model(f"Oil{mode}").get_derivative(time)
    wat = data.get_interpolation_model(f"Wat{mode}").get_derivative(time)
    gas = data.get_interpolation_model(f"Gas{mode}").get_derivative(time)
    if wefac is not None:
        oil, wat, gas = oil / wefac, wat / wefac, gas / wefac
    return oil, wat, gas


def pressure(
    data: CumWellData,
    time: TimeVector,
) -> Tuple[TimeSeries, TimeSeries]:
    bhp = data.get_interpolation_model("BHP").get_value(time) * 10
    thp = data.get_interpolation_model("THP").get_value(time) * 10
    return bhp, thp


def flag(
    status: StatusVector,
    time: TimeVector,
    mode: str = "Prod",
) -> TimeSeries:
    model = InterpolationModel(status.get_last_mode(), kind="zero")
    value = model.get_value(time)
    if mode == "Prod":
        bool_value = value.values == 1
    elif mode == "Inj":
        bool_value = value.values == -1
    else:
        raise KeyError()

    return TimeSeries(value.get_time(), bool_value)


def get_fluid_type(
    oil: TimeSeries,
    wat: TimeSeries,
    gas: TimeSeries,
) -> np.ndarray:

    mults = (
        (oil.values != 0).astype(int)
        + (wat.values != 0).astype(int)
        + (gas.values != 0).astype(int)
    ) > 1

    pattern = np.zeros(oil.values.shape) * np.NAN
    pattern = pattern.astype(object)
    pattern[wat.values != 0] = "WAT"
    pattern[oil.values != 0] = "OIL"
    pattern[gas.values != 0] = "GAS"
    pattern[mults] = "MULTI"
    pattern = __fill_forward(pd.DataFrame(pattern)).values
    pattern = pattern.astype(str)
    return pattern


def share(
    oil: TimeSeries,
    wat: TimeSeries,
    gas: TimeSeries,
    pattern: np.ndarray,
    target_phase: str,
) -> TimeSeries:
    total = oil + wat + gas
    if target_phase == "oil":
        results = oil / total
        results[pattern != "MULTI"] = np.NAN
        return results
    elif target_phase == "wat":
        results = wat / total
        results[pattern != "MULTI"] = np.NAN
        return results
    elif target_phase == "gas":
        results = gas / total
        results[pattern != "MULTI"] = np.NAN
        return results
    else:
        raise KeyError


class ConvertorToCumData:
    def __init__(self, method: str = "rectangle") -> None:
        self.Method = method

    @staticmethod
    def __calculate_rectangle(
        data: pd.DataFrame,
        time: TimeVector,
    ) -> pd.DataFrame:
        values = data.values * np.array([time.get_periods()]).T
        new = np.zeros(data.values.shape)
        new[1:] = values[:-1]
        new = new.cumsum(0)
        data.loc[:, :] = new
        return data

    @staticmethod
    def __trapeze_rectangle(data: pd.DataFrame) -> TimeSeries:
        pass

    def __calc(self, data: pd.DataFrame, time: TimeVector) -> pd.DataFrame:
        if self.Method == "rectangle":
            return self.__calculate_rectangle(data, time)
        else:
            raise KeyError

    def do(self, data: WellMeasurement) -> CumWellData:
        data = filing_rates(data)
        time = data.get_time()
        df = data.DataFrame
        rdf = df.loc[:, data.ProdList + data.INJList]
        rdf = self.__calc(rdf, time)
        df.loc[:, data.ProdList + data.INJList] = rdf

        return CumWellData(time, df.values)


class WellHistory:
    def __init__(
        self,
        well_name: str,
        measurement: WellMeasurement,
        history_of_constructions: ConstructionHistory = None,
        prod_mode: WellControlMode = None,
        inj_mode: WellControlMode = None,
        prod_stop_event: StopEventSetting = None,
        wefac: bool = None,
        inj_stop_event: StopEventSetting = None,
        # force_event: = None,
        additional_events: ScheduleDataframe = None,
        add_event_flag: bool = True,
    ) -> None:
        self.WellName = well_name
        self.Measurement = measurement
        self.Constructions = history_of_constructions
        self.AddEVFlag = add_event_flag

        if prod_mode is not None:
            self.ProdMode = prod_mode
        else:
            self.ProdMode = WellControlMode("LRAT")

        if inj_mode is not None:
            self.InjMode = inj_mode
        else:
            self.InjMode = WellControlMode("RATE")

        if prod_stop_event is not None:
            self.ProdEvent = prod_stop_event
        else:
            self.ProdEvent = StopEventSetting(False)

        if inj_stop_event is not None:
            self.InjEvent = inj_stop_event
        else:
            self.InjEvent = StopEventSetting(False)

        if wefac is not None:
            self.WEFAC = wefac
        else:
            self.WEFAC = False

        self.AdditionalEvents = additional_events

    def __repr__(self) -> str:
        return f"WellHistory {self.WellName}"

    def get_time_vector(self, step: str, value_step: int = None) -> TimeVector:
        tv_min, tv_max = self.get_time_limit()
        return generate_time_vector(tv_min, tv_max, step, value_step)

    def get_vfp_number(self, tv: TimeVector) -> TimeSeries:
        if self.Constructions is not None:
            return self.Constructions.VFP.get_value(tv)

    def get_events(self) -> TimeVector:
        status = self.Measurement.get_status()
        event_time = status.get_event_time()
        prod_event = self.ProdEvent.get_value(event_time)
        inj_event = self.InjEvent.get_value(event_time)
        mode_event = status.get_change_event_time()
        mode_event.extend(prod_event.get_time())
        mode_event.extend(inj_event.get_time())
        return mode_event

    def get_time_limit(self) -> Tuple[TimePoint, TimePoint]:
        return self.Measurement.get_time_limits()

    def get_wconhist(
        self,
        tv: TimeVector,
        wefac_falg: bool = False,
        wefac: TimeSeries = None,
        data: CumWellData = None,
    ) -> ScheduleSheet:
        wconhist = ScheduleSheet(EclipseScheduleNames.WCONHIST)

        if data is None:
            data = ConvertorToCumData().do(self.Measurement)

        status = flag(data.get_status(), tv, "Prod")
        if wefac_falg:
            if wefac is None:
                wefac = self.__get_wefac(tv, data)
        else:
            wefac = None

        oil, wat, gas = rates(data, tv, "Prod", wefac)
        bhp, thp = pressure(data, tv)

        wconhist.Time = tv.to_timestamp()
        wconhist.WellName = self.WellName
        wconhist.WellControl = self.ProdMode.get_value(tv).values
        wconhist.OperatingModes = operation(oil, wat, gas).values
        wconhist.OilFlowRate = oil.values
        wconhist.WaterFlowRate = wat.values
        wconhist.GasFlowRate = gas.values
        wconhist.THP = thp.values
        wconhist.BHP = bhp.values
        wconhist.VFP = self.get_vfp_number(tv).values

        wconhist = wconhist[status.Data.values]
        return wconhist

    def get_wconinj(
        self,
        tv: TimeVector,
        wefac_falg: bool = False,
        wefac: TimeSeries = None,
        data: CumWellData = None,
    ) -> ScheduleSheet:
        hist = ScheduleSheet(EclipseScheduleNames.WCONINJH)

        if data is None:
            data = ConvertorToCumData().do(self.Measurement)

        status = flag(data.get_status(), tv, "Inj")

        if wefac_falg:
            if wefac is None:
                wefac = self.__get_wefac(tv, data)
        else:
            wefac = None

        oil, wat, gas = rates(data, tv, "Inj", wefac)
        bhp, thp = pressure(data, tv)

        hist.Time = tv.to_timestamp()
        hist.WellName = self.WellName
        hist.FluidType = get_fluid_type(oil, wat, gas)
        hist.OperatingModes = operation(oil, wat, gas).values
        hist.VolumeInPlace = (oil + wat + gas).values
        hist.THP = thp.values
        hist.BHP = bhp.values
        hist.VFR = self.get_vfp_number(tv).values
        ft = hist.FluidType
        hist.OilInRate = share(oil, wat, gas, ft, "wat").values
        hist.WaterInRate = share(oil, wat, gas, ft, "gas").values
        hist.GasInRate = share(oil, wat, gas, ft, "oil").values
        hist.WellControl = self.InjMode.get_value(tv).values

        hist = hist[status.Data.values]
        return hist

    def __get_wefac(
        self,
        tv: TimeVector,
        data: CumWellData = None,
    ) -> TimeSeries:
        if data is None:
            data = ConvertorToCumData().do(self.Measurement)
        status = data.get_status()
        wefac = status.get_wefac(tv)
        wefac[wefac == 0] = 1
        return wefac

    def get_wefac(
        self,
        tv: TimeVector,
        wefac: TimeSeries = None,
        data: CumWellData = None,
    ) -> ScheduleSheet:
        if wefac is None:
            wefac = self.__get_wefac(tv, data)
        ss = ScheduleSheet(EclipseScheduleNames.WEFAC)
        ss.Time = wefac.get_time().to_timestamp()
        ss.WellName = self.WellName
        ss.ServiceFactor = wefac.values
        return ss

    def get_schedule(self, tv: TimeVector) -> ScheduleDataframe:
        sdf = ScheduleDataframe()
        data = ConvertorToCumData().do(self.Measurement)
        tv = tv.cut(self.Measurement.get_time())
        wefac = self.__get_wefac(tv, data)
        if self.WEFAC:
            sdf = sdf + self.get_wefac(tv, wefac, data)
        sdf = sdf + self.get_wconhist(tv, self.WEFAC, wefac, data)
        sdf = sdf + self.get_wconinj(tv, self.WEFAC, wefac, data)

        if self.AddEVFlag and self.AdditionalEvents is not None:
            sdf = sdf + self.AdditionalEvents

        return sdf

    def presentation(self) -> None:
        HistoryDataPainter().do(self)
