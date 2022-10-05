from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
    from typing import Union, Dict, Tuple, List, Optional, Any

    iter_var = Union[List[str], Tuple[str, ...], np.ndarray, pd.Series]

import numpy as np
import pandas as pd

from scipy.interpolate import interp1d
from copy import deepcopy

from ..Time import TimeVector, TimePoint, TimeDelta


class TimeSeries:
    def __init__(self, time: TimeVector, data: np.ndarray) -> None:
        self.Data = pd.Series(data=data, index=time.to_frame_index())

    def __setitem__(self, key: Any, value: Any) -> None:
        self.Data.iloc[key] = value

    def __getitem__(self, item: Any) -> TimeSeries:
        return TimeSeries(
            self.get_time()[item],
            self.Data.values[item],
        )

    def __eq__(self, other: Any) -> np.ndarray:
        return self.Data.values == other

    def __ne__(self, other: Any) -> np.ndarray:
        return self.Data.values != other

    def __mul__(self, other: Any) -> TimeSeries:
        if type(other) == np.ndarray:
            new = deepcopy(self)
            new.Data.loc[:] = new.Data.values * other
        elif type(other) == pd.Series:
            new = deepcopy(self)
            new.Data.loc[:] = new.Data.values * other.values
        elif type(other) == TimeSeries:
            new = deepcopy(self)
            new.Data.loc[:] = new.Data.values * other.Data.values
        elif type(other) in (float, int):
            new = deepcopy(self)
            new.Data.loc[:] = new.Data.values * other
        else:
            raise TypeError
        return new

    def __sub__(self, other: Any) -> TimeSeries:
        if isinstance(other, TimeSeries):
            new = deepcopy(self)
            new.Data = self.Data - other.Data
            return new
        else:
            raise TypeError

    def __rsub__(self, other: Any) -> TimeSeries:
        if isinstance(other, TimeSeries):
            new = deepcopy(self)
            new.Data = other.Data - self.Data
            return new
        else:
            raise TypeError

    def __add__(self, other: Any) -> TimeSeries:
        if isinstance(other, TimeSeries):
            new = deepcopy(self)
            new.Data = self.Data + other.Data
            return new
        else:
            raise TypeError

    def __truediv__(self, other: Any) -> TimeSeries:
        if isinstance(other, TimeSeries):
            new = deepcopy(self)
            new.Data = self.Data / other.Data
            return new
        elif type(other) == np.ndarray:
            new = deepcopy(self)
            new.Data = self.Data / other
            return new
        else:
            raise TypeError

    def __rtruediv__(self, other: Any) -> Optional[TimeSeries]:
        if isinstance(other, TimeSeries):
            new = deepcopy(self)
            new.Data = self.Data / other.Data
            new.Unit = f"{self.Data}/{other.Data}"
            return new
        elif type(other) == np.ndarray:
            new = deepcopy(self)
            new.Data = self.Data / other
            return None
        else:
            raise TypeError

    def __rdiv__(self, other: Any) -> Optional[TimeSeries]:
        if isinstance(other, TimeSeries):
            new = deepcopy(self)
            new.Data = other.Data / self.Data
            new.Unit = f"{other.Data}/{self.Data}"
            return new
        elif type(other) == np.ndarray:
            new = deepcopy(self)
            new.Data.iloc[:] = other / self.Data.values
            return None
        else:
            raise TypeError

    def __invert__(self) -> TimeSeries:
        new = deepcopy(self)
        new.Data.iloc[:] = self.Data.values is False
        return new

    def __or__(self, other: TimeSeries) -> TimeSeries:
        new = deepcopy(self)
        new.Data.iloc[:] = self.Data.values | other.Data.values
        return new

    def __repr__(self) -> str:
        return f"ParamVector {self.values.shape}"

    def astype(self, dtype: str) -> TimeSeries:
        new = deepcopy(self)
        new.Data = new.Data.astype(dtype=dtype)
        return new

    def shape(self) -> Tuple[int, ...]:
        return self.Data.shape

    def get_time(self) -> TimeVector:
        return TimeVector(self.Data.index.to_numpy())

    @property
    def values(self) -> np.ndarray:
        return self.Data.values

    def series(self) -> pd.Series:
        return self.Data

    def change_times(self) -> Optional[TimeVector]:
        data = self.Data.values
        patten = np.zeros(data.shape) * np.NAN
        patten[:-1] = ~(data[:-1] == data[1:])
        patten[0] = False

        if all(~patten):
            return None

        tv = self.get_time()
        return tv[patten]

    def drop_nan(self) -> Optional[TimeSeries]:
        data = self.Data.dropna()
        if not data.empty:
            return TimeSeries(TimeVector(data.index), data.values)
        else:
            return None

    def cumsum(self) -> TimeSeries:
        new = deepcopy(self)
        new.Data[:] = self.Data.values.cumsum()
        return new

    def cumsum_time(self) -> TimeSeries:
        value = self.Data.values
        tv = self.get_time()
        delta_time = (tv[1:] - tv[:-1]).Delta / np.timedelta64(1, "D")
        delta_val = value[:-1] * delta_time
        cum_val = delta_val.cumsum()
        results_val = np.zeros(value.shape)
        results_val[1:] = cum_val
        return TimeSeries(tv, results_val)

    def to_interpolation_model(
        self,
        step: str = "D",
        kind: str = "linear",
        copy: bool = True,
        bounds_error: Union[bool, str] = True,
        fill_value: Union[Union[float, int], Tuple[float, float]] = np.NAN,
    ) -> InterpolationModel:
        return InterpolationModel(
            self,
            step,
            kind,
            copy,
            bounds_error,
            fill_value,
        )


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


class InterpolationModel:
    def __init__(
        self,
        data: TimeSeries,
        step: str = "D",
        kind: str = "linear",
        # axis: Optional[int] = None,
        copy: bool = True,
        bounds_error: Union[bool, str] = True,
        fill_value: Union[Union[float, int], Tuple[float, float]] = np.NAN,
    ) -> None:
        self.Step = step
        self.StartTime = data.get_time().min

        self.Model = interp1d(
            self.calc_cum_step(data.get_time()),
            data.values,
            kind=kind,
            copy=copy,
            bounds_error=bounds_error,
            fill_value=fill_value,
        )

    @property
    def end_date(self) -> TimePoint:
        max_x = self.Model.x.max()
        int_delta = int(TimeDelta.convert(max_x, self.Step))
        delta = np.timedelta64(int_delta, "ms")
        t = self.StartTime.Date + delta
        return TimePoint(t)

    def calc_cum_step(self, time: TimeVector) -> np.ndarray:
        delta_time = time - self.StartTime
        return delta_time.to_array()

    def get_value(self, time_points: TimeVector) -> TimeSeries:
        cum_time = self.calc_cum_step(time_points)
        values = self.Model(cum_time)
        return TimeSeries(time_points, values)

    def __get_extend_delta(self, time: TimeVector) -> TimeSeries:
        all_value = self.get_value(time)
        start_values = all_value[:-1]
        end_values = TimeSeries(start_values.get_time(), all_value[1:].values)

        delta = np.zeros(time.shape())
        delta[:-1] = end_values.values - start_values.values
        delta[-1] = delta[-2]

        return TimeSeries(time, delta)

    def __get_no_extend_delta(self, time: TimeVector) -> TimeSeries:
        start_values = self.get_value(time[:-1])
        end_values = self.get_value(time[1:])
        delta = end_values.values - start_values.values
        return TimeSeries(time[:-1], delta)

    def get_delta(self, time: TimeVector, extend: bool = True) -> TimeSeries:
        if extend:
            return self.__get_extend_delta(time)
        else:
            return self.__get_no_extend_delta(time)

    def get_derivative(self, time: TimeVector) -> TimeSeries:
        start_values = self.get_value(time[:-1]).values
        end_values = self.get_value(time[1:]).values
        value_delta = end_values - start_values

        time_delta = time.get_periods()
        derivative = np.zeros(time.shape())
        derivative[:-1] = value_delta / time_delta[:-1]
        derivative[-1] = derivative[-2]
        results = TimeSeries(time, derivative)
        return results


class StringInterpolationModel:
    def __init__(
        self,
        mode: Union[bool, str, Dict[TimePoint, Union[str, bool]]],
        step: str = "D",
        # kind: str = "linear",
        # axis: Optional[int] = None,
        # copy: bool = True,
        bounds_error: Union[bool, str] = False,
        # fill_value: Union[Union[float, int], Tuple[float, float]] = np.NAN,
    ) -> None:
        self.Modes = mode
        self.__step = step
        self.__bounds_error = bounds_error
        # self.__init(modes, step, kind, copy, bounds_error, fill_value)

    def __get_value(self, tv: TimeVector) -> TimeSeries:
        keys = tuple(set(self.Modes.keys()))

        if len(keys) == 0:
            raise ValueError
        elif len(keys) == 1:
            value = np.array([self.Modes[keys[0]]] * tv.shape())
            return TimeSeries(tv, value)

        s = pd.Series(self.Modes)
        for kid, key in enumerate(keys):
            s = s.replace(key, kid)
        tvd = TimeVector(s.index)
        pv = TimeSeries(tvd, s.values)

        vmin = s[tvd.min]
        vmax = s[tvd.max]

        models = InterpolationModel(
            data=pv,
            step="D",
            kind="zero",
            # axis,
            # copy,
            bounds_error=False,
            fill_value=(vmin, vmax),
        )
        value = models.get_value(tv)
        s = value.series()

        for kid, key in enumerate(keys):
            s = s.replace(kid, key)

        return TimeSeries(tv, s.values)

    def get_value(self, tv: TimeVector) -> TimeSeries:
        if isinstance(self.Modes, str):
            value = np.array([self.Modes] * tv.shape())
            return TimeSeries(tv, value)
        elif isinstance(self.Modes, bool):
            value = np.array([self.Modes] * tv.shape())
            return TimeSeries(tv, value)
        elif isinstance(self.Modes, dict):
            self.__get_value(tv)
        else:
            raise TypeError
