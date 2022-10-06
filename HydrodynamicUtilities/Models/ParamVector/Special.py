from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Dict, Tuple, List, Optional, Any

import numpy as np
import pandas as pd

from copy import deepcopy

from .Interpolation import TimeSeries, InterpolationModel, StringInterpolationModel
from ..Time import TimeVector, TimePoint, TimeDelta


class StatusVector(TimeSeries):
    def get_downtime_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        results[self.Data.values == 0] = 1
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_work_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        results[self.Data.values != 0] = 1
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_prod_mode_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        results[self.Data.values == 1] = 1
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_inj_mode_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        results[self.Data.values == -1] = 1
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_mode_change_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        value = self.Data.values
        results[1:] = value[1:] != value[:-1]
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_start_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        value = abs(self.Data.values)
        results[1:] = value[1:] != value[:-1]
        results = results * self.get_work_flag().values
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_stop_flag(self) -> TimeSeries:
        results = np.zeros(self.shape())
        value = self.Data.values
        results[1:] = value[1:] != value[:-1]
        results = results * self.get_downtime_flag().values
        return TimeSeries(self.get_time(), results.astype(bool))

    def get_work_time(self) -> TimeSeries:
        time = self.get_time()
        periods = time.get_periods()
        work_periods = periods * abs(self.Data.values)
        cum_value = np.zeros(time.shape())
        cum_value[1:] = work_periods.cumsum()[:-1]
        return TimeSeries(time, cum_value)

    def get_cum_period(self) -> TimeSeries:
        time = self.get_time()
        periods = time.get_periods()
        work_periods = periods
        cum_value = np.zeros(time.shape())
        cum_value[1:] = work_periods.cumsum()[:-1]
        return TimeSeries(time, cum_value)

    def get_last_mode(self) -> StatusVector:
        values = deepcopy(self.Data.values)
        values[values == 0] = np.NAN
        df = pd.Series(values)
        df = df.fillna(method="ffill")
        df = df.fillna(method="bfill")
        return StatusVector(self.get_time(), df.values)

    def get_event_time(self) -> TimeVector:
        mode_flag = self.get_mode_change_flag()
        tv = mode_flag[mode_flag == 1].get_time()
        return tv

    def get_change_event_time(self) -> TimeVector:
        new_status = self.get_last_mode()
        mode_flag = new_status.get_mode_change_flag()
        return mode_flag[mode_flag == 1].get_time()

    def get_interpolation_model(self) -> InterpolationModel:
        return InterpolationModel(
            self,
            step="D",
            kind="zero",
        )

    def get_wefac(self, out_tv: TimeVector) -> TimeSeries:
        work_time_model = InterpolationModel(self.get_work_time())
        tv_model = InterpolationModel(self.get_cum_period())

        work_time = work_time_model.get_delta(out_tv)
        time = tv_model.get_delta(out_tv)

        return work_time / time


class CumTimeSeriasParam(TimeSeries):
    def __init__(self, time: TimeVector, data: np.ndarray) -> None:
        super().__init__(time, data)

    def get_derivative_serias(self, step: str = "D") -> RateTimeSeriasParam:
        val = self.Data.values
        delta_val = val[1:] - val[:-1]

        time = self.get_time()
        step64 = np.timedelta64(1, step)
        delta_time = (time[1:] - time[:-1]).Delta / step64

        results = np.zeros(val.shape)
        results[:-1] = delta_val / delta_time
        results[-1] = results[-1]
        return RateTimeSeriasParam(time, results, step, val[0])

    def get_delta_serias(self, step: str = "D") -> PeriodTimeSeriasParam:
        val = self.Data.values
        delta_val = val[1:] - val[:-1]

        results = np.zeros(val.shape)
        results[:-1] = delta_val
        results[-1] = results[-1]
        return PeriodTimeSeriasParam(self.get_time(), results, step, val[0])

    def retime(self, tv: TimeVector) -> CumTimeSeriasParam:
        value = self.Data.values
        model = InterpolationModel(
            self,
            bounds_error=False,
            fill_value=(value[0], value[-1]),
        )
        new_value = model.get_value(tv)
        return CumTimeSeriasParam(self.get_time(), new_value.values)


class PeriodTimeSeriasParam(TimeSeries):
    def __init__(
        self,
        time: TimeVector,
        data: np.ndarray,
        time_step: str = "D",
        start_value: Union[float, int] = 0,
    ) -> None:
        super().__init__(time, data)
        self.TimeStep = time_step
        self.StartValue = start_value

    def get_base_timedelta64(self) -> np.timedelta64:
        return np.timedelta64(1, self.TimeStep)

    def get_cum_serias(self) -> CumTimeSeriasParam:
        value = self.Data.values
        cum_value = value.cumsum()
        results = np.ones(value.shape) * self.StartValue
        results[1:] = cum_value[:-1]
        return CumTimeSeriasParam(self.get_time(), results)

    def get_derivative_serias(self, step: str = "D") -> RateTimeSeriasParam:
        delta_val = self.Data.values

        time = self.get_time()
        step64 = np.timedelta64(1, step)
        delta_time = (time[1:] - time[:-1]).Delta / step64
        delta_time = np.concatenate((delta_time, [delta_time[-1]]))

        results = delta_val / delta_time

        return RateTimeSeriasParam(time, results, step, self.StartValue)

    def retime(self, tv: TimeVector) -> PeriodTimeSeriasParam:
        cum_data = self.get_cum_serias()
        new_cum_data = cum_data.retime(tv)
        return new_cum_data.get_delta_serias()


class RateTimeSeriasParam(TimeSeries):
    def __init__(
        self,
        time: TimeVector,
        data: np.ndarray,
        time_step: str = "D",
        start_value: Union[float, int] = 0,
    ) -> None:
        super().__init__(time, data)
        self.TimeStep = time_step
        self.StartValue = start_value

    def get_base_timedelta64(self) -> np.timedelta64:
        return np.timedelta64(1, self.TimeStep)

    def get_cum_serias(self) -> CumTimeSeriasParam:
        value = self.Data.values
        tv = self.get_time()
        delta_time = (tv[1:] - tv[:-1]).Delta / self.get_base_timedelta64()
        delta_val = value[:-1] * delta_time
        cum_val = delta_val.cumsum()
        results_val = np.ones(value.shape) * self.StartValue
        results_val[1:] = results_val[1:] + cum_val
        return CumTimeSeriasParam(tv, results_val)

    def get_period_serias(self) -> PeriodTimeSeriasParam:
        tv = self.get_time()
        delta_time = (tv[1:] - tv[:-1]).Delta / self.get_base_timedelta64()
        delta_time = np.concatenate((delta_time, [delta_time[-1]]))

        value = self.Data.values
        res = value * delta_time
        return PeriodTimeSeriasParam(tv, res, self.TimeStep, self.StartValue)

    def retime(self, tv: TimeVector) -> RateTimeSeriasParam:
        cum_data = self.get_cum_serias()
        new_cum_data = cum_data.retime(tv)
        return new_cum_data.get_derivative_serias()
