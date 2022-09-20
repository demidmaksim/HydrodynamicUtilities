from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicModelAnalysis.Models import TimeVector
    from typing import Tuple

import pandas as pd
import numpy as np

from copy import deepcopy

from HydrodynamicModelAnalysis.Models.DataFile import ScheduleSheet, ScheduleDataframe
from HydrodynamicModelAnalysis.Models.Source import EclipseScheduleNames
from HydrodynamicModelAnalysis.Models import (
    TimeSeries,
    InterpolationModel,
    StatusVector,
)
from HydrodynamicModelAnalysis.Models import WellMeasurement, CumWellData


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

        if param in changed.ProdList:
            value = value * data.get_status().get_prod_mode_flag()
        elif param in changed.INJList:
            value = value * data.get_status().get_inj_mode_flag()

        setattr(changed, param, value)

    return changed


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


class ConvertToWCONHIST:
    @staticmethod
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

    @staticmethod
    def rates(
        data: CumWellData,
        time: TimeVector,
        mode: str = "Prod",
    ) -> Tuple[TimeSeries, TimeSeries, TimeSeries]:
        oil = data.get_interpolation_model(f"Oil{mode}").get_derivative(time)
        wat = data.get_interpolation_model(f"Wat{mode}").get_derivative(time)
        gas = data.get_interpolation_model(f"Gas{mode}").get_derivative(time)
        return oil, wat, gas

    @staticmethod
    def pressure(
        data: CumWellData,
        time: TimeVector,
    ) -> Tuple[TimeSeries, TimeSeries]:
        bhp = data.get_interpolation_model("BHP").get_value(time) * 10
        thp = data.get_interpolation_model("THP").get_value(time) * 10
        return bhp, thp

    @staticmethod
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

    def new_convert_prod(
        self,
        data: CumWellData,
        time: TimeVector,
        well_name: str,
        method: WellModeSetting,
    ) -> ScheduleSheet:
        wconhist = ScheduleSheet(EclipseScheduleNames.WCONHIST)

        bt = data.get_time()
        time = time.cut(bt)

        status = self.flag(data.get_status(), time, "Prod")
        oil, wat, gas = self.rates(data, time, "Prod")
        bhp, thp = self.pressure(data, time)

        wconhist.Time = time.to_timestamp()
        wconhist.ObjectName = well_name
        wconhist.WellControl = method.get_values(time)[0]
        wconhist.OperatingModes = self.operation(oil, wat, gas).values
        wconhist.OilFlowRate = oil.values
        wconhist.WaterFlowRate = wat.values
        wconhist.GasFlowRate = gas.values
        wconhist.THP = thp.values
        wconhist.BHP = bhp.values

        wconhist = wconhist[status.Data.values]
        return wconhist


class ConvertToWCONINJH(ConvertToWCONHIST):
    @staticmethod
    def __get_fluid_type(
        oil: TimeSeries,
        wat: TimeSeries,
        gas: TimeSeries,
    ) -> np.ndarray:

        mults = ((oil.values != 0) + (wat.values != 0) + (gas.values != 0)) > 1
        pattern = np.zeros(oil.values.shape)
        pattern = pattern.astype(str)
        pattern[:] = "WAT"
        pattern[oil.values != 0] = "OIL"
        pattern[gas.values != 0] = "GAS"
        pattern[mults] = "MULTI"

        return pattern

    @staticmethod
    def __share(
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

    def convert_inj(
        self,
        data: CumWellData,
        time: TimeVector,
        well_name: str,
        method: str,
    ) -> ScheduleSheet:
        hist = ScheduleSheet(EclipseScheduleNames.WCONINJH)

        time = time.cut(data.get_time())

        status = self.flag(data.get_status(), time, "Inj")
        oil, wat, gas = self.rates(data, time, "Inj")
        bhp, thp = self.pressure(data, time)

        hist.Time = time.to_timestamp()
        hist.ObjectName = well_name
        hist.FluidType = self.__get_fluid_type(oil, wat, gas)
        hist.OperatingModes = self.operation(oil, wat, gas).values
        hist.VolumeInPlace = (oil + wat + gas).values
        hist.THP = thp.values
        hist.BHP = bhp.values
        ft = hist.FluidType
        hist.OilInRate = self.__share(oil, wat, gas, ft, "wat").values
        hist.WaterInRate = self.__share(oil, wat, gas, ft, "gas").values
        hist.GasInRate = self.__share(oil, wat, gas, ft, "oil").values
        hist.WellControl = method

        hist = hist[status.Data.values]
        return hist

    def new_convert_inj(
        self,
        data: CumWellData,
        time: TimeVector,
        well_name: str,
        method: WellModeSetting,
    ) -> ScheduleSheet:
        hist = ScheduleSheet(EclipseScheduleNames.WCONINJH)

        time = time.cut(data.get_time())

        status = self.flag(data.get_status(), time, "Inj")
        oil, wat, gas = self.rates(data, time, "Inj")
        bhp, thp = self.pressure(data, time)

        hist.Time = time.to_timestamp()
        hist.ObjectName = well_name
        hist.FluidType = self.__get_fluid_type(oil, wat, gas)
        hist.OperatingModes = self.operation(oil, wat, gas).values
        hist.VolumeInPlace = (oil + wat + gas).values
        hist.THP = thp.values
        hist.BHP = bhp.values
        ft = hist.FluidType
        hist.OilInRate = self.__share(oil, wat, gas, ft, "wat").values
        hist.WaterInRate = self.__share(oil, wat, gas, ft, "gas").values
        hist.GasInRate = self.__share(oil, wat, gas, ft, "oil").values
        hist.WellControl = method.get_values(time)[1]

        hist = hist[status.Data.values]
        return hist


class NewHistoryConvertor:
    @classmethod
    def convert(cls, hdata: FieldHistory) -> ScheduleDataframe:

        wconhist = ScheduleSheet(EclipseScheduleNames.WCONHIST)
        wconinjh = ScheduleSheet(EclipseScheduleNames.WCONINJH)
        sdf = ScheduleDataframe()

        tv = hdata.get_time_vector()

        for wname, whdata in hdata:
            wchdata = ConvertorToCumData().do(whdata.Data)
            whmode = whdata.ModeSetting

            hist_convertor = ConvertToWCONHIST().new_convert_prod
            wconhist = wconhist + hist_convertor(wchdata, tv, wname, whmode)

            hist_convertor = ConvertToWCONINJH().new_convert_inj
            wconinjh = wconinjh + hist_convertor(wchdata, tv, wname, whmode)

        sdf.WCONHIST = wconhist
        sdf.WCONINJH = wconinjh

        return sdf
