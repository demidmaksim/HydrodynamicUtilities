from __future__ import annotations

import numpy as np
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Any, Optional, List, Iterator, Tuple, Dict
    from datetime import datetime

    valid_formats = Union[
        np.datetime64,
        str,
        datetime,
    ]

    numbers = Union[
        float,
        int,
        np.float16,
        np.int16,
        np.float32,
        np.int32,
        np.float64,
        np.int64,
    ]

    delta_format = Union[
        np.ndarray,
        numbers,
        List[Union[numbers]],
        Tuple[Union[numbers]],
    ]

import datetime as dt

from .Point import TimePoint
from copy import deepcopy


class TimeVectorConstructor:
    @staticmethod
    def from_ndarray(data: np.ndarray) -> np.ndarray:
        return data.astype(dtype="datetime64[ms]")

    @staticmethod
    def from_string_list(data: List[str]) -> np.ndarray:
        if any(pd.isna(data)):
            true_pattern = pd.isna(data)
            value = np.array(data)[~true_pattern].astype("datetime64[ms]")
            results = np.zeros(len(data))
            results[:] = np.datetime64("NAT")
            results = results.astype("datetime64[ms]")
            results[~true_pattern] = value
            return results
        else:
            results = np.array(data).astype("datetime64[ms]")
            return results

    @classmethod
    def from_pandas_index(cls, data: pd.Index) -> np.ndarray:
        return cls.from_ndarray(data.to_numpy())

    @classmethod
    def from_datetime_index(cls, data: pd.DatetimeIndex) -> np.ndarray:
        return cls.from_ndarray(data.to_numpy())

    @classmethod
    def create(cls, data: Union[np.ndarray, List[str]]) -> np.ndarray:
        if type(data) == np.ndarray:
            return cls.from_ndarray(data)
        elif type(data) == list:
            return cls.from_string_list(data)
        # elif type(data) == pd.Index:
        #     return cls.from_pandas_index(data)
        elif isinstance(data, pd.DatetimeIndex):
            return cls.from_datetime_index(data)
        elif isinstance(data, pd.Series):
            return cls.from_ndarray(data.values)
        else:
            raise TypeError


class TimeVector:
    def __init__(
        self,
        data: Union[np.ndarray, List[str], pd.Index],
    ) -> None:
        self.Dates: np.ndarray = TimeVectorConstructor.create(data)

    def __repr__(self) -> str:
        return f"TimeVector {len(self.Dates)}"

    def __iter__(self) -> Iterator[np.datetime64]:
        return iter(self.to_datetime64())

    def __getitem__(self, item: Any) -> Optional[TimeVector, TimePoint]:
        days = self.Dates[item]
        if type(days) == np.ndarray:
            return TimeVector(days)
        else:
            return TimePoint(days)

    def __contains__(self, item: Union[np.datetime64, TimePoint]) -> bool:
        if type(item) == np.datetime64:
            return item in self.Dates
        elif type(item) == np.datetime64:
            return item.Date in self.Dates
        else:
            raise TypeError

    @staticmethod
    def __choose(other: Union[TimePoint, np.datetime64]) -> np.datetime64:
        if type(other) == TimePoint:
            return other.Date
        elif type(other) == np.datetime64:
            return other
        else:
            raise TypeError

    def __eq__(self, other: Union[TimePoint, np.datetime64]) -> bool:
        point = self.__choose(other)
        return self.Dates == point

    def __ne__(self, other: Union[TimePoint, np.datetime64]) -> bool:
        point = self.__choose(other)
        return self.Dates != point

    def __lt__(self, other: Union[TimePoint, np.datetime64]) -> bool:
        point = self.__choose(other)
        return self.Dates < point

    def __gt__(self, other: Union[TimePoint, np.datetime64]) -> bool:
        point = self.__choose(other)
        return self.Dates > point

    def __le__(self, other: Union[TimePoint, np.datetime64]) -> bool:
        point = self.__choose(other)
        return self.Dates <= point

    def __ge__(self, other: Union[TimePoint, np.datetime64]) -> bool:
        point = self.__choose(other)
        return self.Dates >= point

    def __add__(self, other: TimeDelta) -> TimeVector:
        return other.__add__(self)

    def __radd__(self, other: TimeDelta) -> TimeVector:
        return other.__radd__(self)

    def __sub__(
        self,
        other: Union[TimeVector, TimeDelta, TimePoint],
    ) -> Union[TimeVector, TimeDelta]:
        if type(other) == TimeDelta:
            return TimeVector(self.Dates - other.Delta)
        elif type(other) == TimeVector:
            delta = self.Dates - other.Dates
            delta = delta.astype("timedelta64[ms]")
            return TimeDelta(delta, "ms")
        elif type(other) == TimePoint:
            delta = self.Dates - other.Date
            delta = delta.astype("timedelta64[ms]")
            return TimeDelta(delta, "ms")

    def __rsub__(self, other: Union[TimeVector, TimePoint]) -> TimeDelta:
        if type(other) == TimeVector:
            delta = other.Dates - self.Dates
            delta = delta.astype("timedelta64[ms]")
            return TimeDelta(delta, "ms")
        elif type(other) == TimePoint:
            delta = self.Dates - other.Date
            delta = delta.astype("timedelta64[ms]")
            return TimeDelta(delta, "ms")

    @property
    def min(self) -> TimePoint:
        return TimePoint(min(self.Dates))

    @property
    def max(self) -> TimePoint:
        return TimePoint(max(self.Dates))

    def shape(self) -> int:
        return len(self.Dates)

    def __unique(self) -> np.ndarray:
        return pd.unique(self.Dates)

    def unique(self, in_place: bool = False) -> Optional[TimeVector]:
        if in_place:
            self.Dates = self.__unique()
            return None
        else:
            return TimeVector(self.__unique())

    def sort(self, in_place: bool = False) -> Optional[TimeVector]:
        if in_place:
            self.Dates.sort()
            return None
        else:
            return TimeVector(np.sort(self.Dates))

    def extend(self, other: TimeVector) -> None:
        self.Dates = np.concatenate((self.Dates, other.Dates))
        self.unique(in_place=True)
        self.sort(in_place=True)

    def append(self, other: TimePoint) -> None:
        t = np.array([other.to_datetime64()])
        self.Dates = np.concatenate((self.Dates, t))
        self.unique(in_place=True)
        self.sort(in_place=True)

    def get_copy(self) -> TimeVector:
        return deepcopy(self)

    def to_datetime64(self) -> np.ndarray:
        return self.Dates

    def to_timestamp(self) -> pd.Series:
        datetime64 = self.to_datetime64()
        series = pd.Series(datetime64, dtype="datetime64[ms]")
        return series

    def to_frame_index(self) -> pd.Index:
        time_stamp = self.to_timestamp()
        return pd.Index(time_stamp)

    def to_string_list(self) -> List[str]:
        date = self.to_datetime64()
        date = date.astype(dtype="datetime64[s]")
        results = []
        for time_point in date:
            results.append(str(time_point))
        return results

    def to_datetime_list(self) -> List[Optional[dt.datetime]]:
        results = []
        pattern = "%Y-%m-%dT%H:%M:%S"
        for string_time_point in self.to_string_list():
            try:
                time_point = dt.datetime.strptime(string_time_point, pattern)
            except ValueError:
                time_point = None
            results.append(time_point)
        return results

    def to_eclipse_schedule_list(self) -> List[str]:
        results = []
        pattern = "%d %b %Y %H:%M:%S"
        for time_point in self.to_datetime_list():
            results.append(time_point.strftime(pattern))
        return results

    def get_array_delta(
        self,
        time_point: TimePoint,
        steptype: str = "D",
    ) -> np.ndarray:
        # TODO
        pass

    def get_periods(self) -> np.ndarray:
        delta = np.zeros(self.Dates.shape)
        delta[:-1] = self.Dates[1:] - self.Dates[:-1]
        delta[-1] = delta[-2]
        delta = delta.astype("timedelta64[ms]")
        delta = delta / np.timedelta64(1, "D")
        return delta

    def upscaling(self, method: str, value: int) -> TimeVector:
        min_value = self.min.to_datetime64()
        max_value = self.max.to_datetime64()
        dt = f"datetime64[{method}]"
        dates = np.arange(min_value, max_value, dtype=dt, step=value)
        dates = dates.astype(dtype="datetime64[ms]")
        dates[0] = min_value
        dates = np.concatenate((dates, np.array([max_value])))
        return TimeVector(dates)

    def cut(self, other: TimeVector) -> TimeVector:
        value = self.to_datetime64()

        if self.max > other.max:
            pattern = value < other.max.Date
            value = value[pattern]
            value = np.concatenate((value, [other.max.Date]))

        if self.min < other.min:
            pattern = value > other.min.Date
            value = value[pattern]
            value = np.concatenate(([other.min.Date], value))

        return TimeVector(value)


class TimeDelta:
    def __init__(
        self,
        delta: delta_format,
        datatype: str = "D",
    ) -> None:
        if type(delta) in (float, int):
            delta = np.array([delta])
        elif type(delta) in (list, tuple):
            delta = np.array([delta])

        value = self.convert(delta, datatype)

        if isinstance(
            value,
            (
                float,
                int,
                np.float16,
                np.int16,
                np.float32,
                np.int32,
                np.float64,
                np.int64,
            ),
        ):
            value = np.array([value])

        p = pd.Series(value).isna().values
        if not all(~p):
            value[p] = "NaT"

        value[~p] = value[~p].astype(np.int64)
        self.Delta = value.astype(f"timedelta64[ms]")

    @staticmethod
    def convert(delta: delta_format, datatype: str) -> delta_format:
        if datatype.lower() == "y":
            value = delta * 365 * 24 * 3600 * 1000 // 1
        elif datatype.lower() == "m":
            value = delta * 30 * 24 * 3600 * 1000 // 1
        elif datatype.lower() == "w":
            value = delta * 7 * 24 * 3600 * 1000 // 1
        elif datatype.lower() == "d":
            value = delta * 24 * 3600 * 1000 // 1
        elif datatype.lower() == "h":
            value = delta * 3600 * 1000 // 1
        elif datatype.lower() == "m":
            value = delta * 60 * 1000 // 1
        elif datatype.lower() == "s":
            value = delta * 1000 // 1
        elif datatype.lower() == "ms":
            value = delta // 1
        else:
            raise KeyError

        return value

    def __repr__(self) -> str:
        return f"TimeDelta {self.Delta.shape}"

    def __eq__(self, other: TimeDelta) -> bool:
        return self.Delta == other.Delta

    def __ne__(self, other: TimeDelta) -> bool:
        return self.Delta != other.Delta

    def __lt__(self, other: TimeDelta) -> bool:
        return self.Delta < other.Delta

    def __gt__(self, other: TimeDelta) -> bool:
        return self.Delta > other.Delta

    def __le__(self, other: TimeDelta) -> bool:
        return self.Delta <= other.Delta

    def __ge__(self, other: TimeDelta) -> bool:
        return self.Delta >= other.Delta

    def __add__(
        self,
        other: Union[TimeDelta, TimeVector, TimePoint],
    ) -> Union[TimeDelta, TimeVector]:
        if type(other) == TimeDelta:
            return TimeDelta(
                delta=self.Delta + other.Delta,
                datatype="ms",
            )
        elif type(other) == TimeDelta:
            return TimeVector(other.Dates + self.Delta)

        elif type(other) == TimePoint:
            return TimeVector(other.Date + self.Delta)
        else:
            raise TypeError

    def __sub__(
        self,
        other: TimeDelta,
    ) -> TimeDelta:
        return TimeDelta(
            delta=self.Delta - other.Delta,
            datatype="ms",
        )

    def __mul__(self, other: Union[TimeDelta, float, int]) -> TimeDelta:
        if type(other) == TimeDelta:
            return TimeDelta(
                delta=self.Delta * other.Delta,
                datatype="ms",
            )
        elif type(other) in (float, int):
            return TimeDelta(
                delta=self.Delta * other,
                datatype="ms",
            )
        else:
            raise NotImplementedError

    def __truediv__(self, other: Union[TimeDelta, float, int]) -> TimeDelta:
        if type(other) == TimeDelta:
            return TimeDelta(
                delta=self.Delta / other.Delta,
                datatype="ms",
            )
        elif type(other) in (float, int):
            return TimeDelta(
                delta=self.Delta / other,
                datatype="ms",
            )
        else:
            raise NotImplementedError

    def __radd__(
        self,
        other: Union[TimeDelta, TimeVector, TimePoint],
    ) -> Union[TimeDelta, TimeVector, TimePoint]:
        return self.__add__(other)

    def __rsub__(
        self,
        other: Union[TimeDelta, TimeVector],
    ) -> Union[TimeDelta, TimeVector]:
        if type(other) == TimeDelta:
            return TimeDelta(
                delta=other.Delta - self.Delta,
                datatype="ms",
            )
        elif type(other) == TimeDelta:
            return TimeVector(other.Dates - self.Delta)

    def to_array(self, steptype: str = "D") -> np.array:
        return self.Delta / np.timedelta64(1, steptype)

    def get_cumsum(self, step: str = "D") -> np.ndarray:
        d = self.Delta / np.timedelta64(1, step)
        return d.cumsum()


def easter_egg(
    start: Union[np.datetime64, str],
    end: Union[np.datetime64, str],
) -> np.ndarray:
    start = np.datetime64(start)
    end = np.datetime64(end)

    start_y = start.astype("datetime64[Y]").astype(int) + 1970

    if start < np.datetime64(f"{start_y}-12-04"):
        ee_start = start_y
    else:
        ee_start = start_y + 1

    end_y = end.astype("datetime64[Y]").astype(int) + 1970

    if end > np.datetime64(f"{end_y}-12-04"):
        ee_end = end_y
    else:
        ee_end = end_y - 1

    results = []
    for years in range(ee_start, ee_end + 1):
        results.append(np.datetime64(f"{years}-12-04"))

    return np.array(results)


def generate_time_vector(
    start: TimePoint,
    end: TimePoint,
    step: str,
    value_step: int = None,
    easter_egg_flag: bool = False,
    flat_borders: bool = False,
) -> TimeVector:
    start = start.Date
    end = end.Date

    if flat_borders:
        all_steps = ("Y", "M", "D", "h", "m", "s", "ms")
        if step != "Y":
            ts = all_steps[all_steps.index(step)]
            ts1 = all_steps[all_steps.index(step) - 1]
        else:
            ts = step
            ts1 = step

        start = start.astype(dtype=f"datetime64[{ts1}]")
        start = start.astype(dtype=f"datetime64[{ts}]")

        end = end.astype(dtype=f"datetime64[{ts1}]") + 1
        end = end.astype(dtype=f"datetime64[{ts}]")

    if value_step is not None:
        dtype = f"datetime64[{step}]"
        vector = np.arange(start, end, dtype=dtype, step=value_step)
    else:
        vector = np.arange(start, end, dtype=f"datetime64[{step}]")
    vector = vector.astype(dtype=f"datetime64[s]")
    vector = vector[1:]
    vector = np.concatenate((vector, [np.datetime64(start), np.datetime64(end)]))

    if easter_egg_flag:
        easter_egg_time_vector = easter_egg(start, end)
        if easter_egg_time_vector is not None:
            vector = np.concatenate((vector, easter_egg_time_vector))
            v = pd.Series(vector)
            v = pd.Series(pd.unique(v))
            vector = v.sort_values()
        results = TimeVector(vector.values)
        results = results.sort()
        results = results.unique()
        return results
    results = TimeVector(vector)
    results = results.sort()
    results = results.unique()
    return results


class NonLinearTime:
    def __init__(
        self,
        start: TimePoint,
        finish: TimePoint,
        base_step: Tuple[str, int],
        additional_control: Dict[TimePoint, Tuple[str, int]] = None,
    ) -> None:
        self.Start = start
        self.Finish = finish
        self.BaseStep = base_step
        if additional_control is not None:
            self.AdditionalControl = additional_control
        else:
            self.AdditionalControl = dict()

    def get_time_vector(self) -> Optional[TimeVector]:
        time = list(self.AdditionalControl.keys())
        time.append(self.Start)
        time.append(self.Finish)
        time.sort()

        results = None

        for tpid, tp in enumerate(time[:-1]):
            if tp in list(self.AdditionalControl.keys()):
                step = self.AdditionalControl[tp]
            else:
                step = self.BaseStep

            next_tp = time[tpid + 1]
            s_type = step[0]
            s_number = step[1]

            if results is None:
                results = generate_time_vector(tp, next_tp, s_type, s_number)
            else:
                new = generate_time_vector(tp, next_tp, s_type, s_number)
                results.extend(new)

        return results
