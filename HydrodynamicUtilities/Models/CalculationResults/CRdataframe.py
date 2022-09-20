from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Optional
    from ..Time import TimeVector
    from pathlib import Path

import pandas as pd
import numpy as np
from copy import deepcopy
from ..ParamVector import InterpolationModel, TimeSeries
from ..Time import TimeVector


class CalcResults:
    CalcName = "Имя модели"
    ObjectName = "Имя объекта"
    ParamName = "Имя параметра"
    TimeMoment = "Момент времени"
    Unit = "Ед. изм."
    Num = "Доп. Номер"
    Value = "Значение"

    _columns = (
        CalcName,
        ObjectName,
        ParamName,
        TimeMoment,
        Unit,
        Num,
        Value,
    )

    def __init__(self) -> None:
        self.df = pd.DataFrame(columns=self._columns)

    def __iter__(self) -> CalcResults:
        df = self.report()

        for rid, row in df.iterrows():
            calc_name = row[self.CalcName]
            object_name = row[self.ObjectName]
            parameter = row[self.ParamName]
            num = row[self.Num]
            yield self.get(calc_name, object_name, parameter, num)

    def __repr__(self) -> str:
        return f"CalcResults {self.df.shape}"

    def get_time(self) -> TimeVector:
        return TimeVector(self.df[self.TimeMoment])

    def append(
        self,
        calc_name: Union[np.ndarray, List[str], str],
        well_name: Union[np.ndarray, List[str], str],
        param_name: Union[np.ndarray, List[str], str],
        num: Union[np.ndarray, List[int], int],
        unit_name: Union[np.ndarray, List[str], str],
        time_moment: TimeVector,
        value: np.ndarray,
    ) -> None:
        df = pd.DataFrame()
        df[self.Value] = value
        df[self.CalcName] = calc_name
        df[self.ObjectName] = well_name
        df[self.ParamName] = param_name
        df[self.Num] = num
        df[self.Unit] = unit_name
        df[self.TimeMoment] = time_moment.to_timestamp()

        self.df = pd.concat((self.df, df), ignore_index=True)

    def report(self) -> pd.DataFrame:
        results = deepcopy(self.df)
        results = results.drop(self.TimeMoment, axis=1)
        results = results.drop(self.Value, axis=1)
        results = results.drop_duplicates()
        return results

    def extend(self, data: CalcResults) -> None:
        self.df = pd.concat((self.df, data.df))

    def calc_names(self) -> List[str]:
        return list(pd.unique(self.df[self.CalcName]))

    def object_names(self) -> List[str]:
        return list(pd.unique(self.df[self.ObjectName]))

    def parameters(self) -> List[str]:
        return list(pd.unique(self.df[self.ParamName]))

    def nums(self) -> List[int]:
        return list(pd.unique(self.df[self.Num]))

    def number_unique_record(self) -> int:
        df = self.report()
        return len(df.index)

    def get(
        self,
        calc_name: str,
        object_name: str,
        parameter: str,
        num: int,
    ) -> CalcResults:
        new_df = deepcopy(self.df)
        new_df = new_df[new_df[self.CalcName] == calc_name]
        new_df = new_df[new_df[self.ObjectName] == object_name]
        new_df = new_df[new_df[self.ParamName] == parameter]
        new_df = new_df[new_df[self.Num] == num]
        results = CalcResults()
        results.df = new_df
        return results

    def to_inter_model(self) -> ModelCalcResults:
        results = ModelCalcResults()

        for part in self:
            if part.number_unique_record() != 1:
                raise ValueError

            value = part.df[self.Value]
            ts = TimeSeries(part.get_time(), value.values)

            models = InterpolationModel(
                ts,
                bounds_error=False,
                fill_value=(value.values[0], value.values[-1]),
            )

            results.append(
                part.df[self.CalcName].values[0],
                part.df[self.ObjectName].values[0],
                part.df[self.ParamName].values[0],
                part.df[self.Num].values[0],
                part.df[self.Unit].values[0],
                models,
            )

        return results

    def to_excel(self, name: Union[Path, str]) -> None:
        self.df.to_excel(name)


class ModelCalcResults:
    CalcName = "Имя модели"
    ObjectName = "Имя объекта"
    ParamName = "Имя параметра"
    Unit = "Ед. изм."
    Num = "Доп. Номер"
    Value = "Значение"

    def __init__(self) -> None:
        self.df = pd.DataFrame()

    def __repr__(self) -> str:
        return f"ModelCalcResults {self.df.shape}"

    def append(
        self,
        calc_name: str,
        well_name: str,
        param_name: str,
        num: int,
        unit_name: str,
        value: InterpolationModel,
    ) -> None:
        df = pd.DataFrame()
        df[self.CalcName] = [calc_name]
        df[self.ObjectName] = well_name
        df[self.ParamName] = param_name
        df[self.Num] = num
        df[self.Unit] = unit_name
        df[self.Value] = value
        self.df = pd.concat((self.df, df))

    def to_period_results(self, time: TimeVector) -> PeriodCalcResults:
        results = PeriodCalcResults()
        for rid, row in self.df.iterrows():

            results.append(
                calc_name=row[self.CalcName],
                period_name=time.to_timestamp()[:-1].values,
                start_period=time.to_timestamp()[:-1].values,
                end_period=time.to_timestamp()[1:].values,
                object_name=row[self.ObjectName],
                param_name=row[self.ParamName],
                unit=row[self.Unit],
                num=row[self.Num],
                value=row[self.Value].get_delta(time, False).values,
            )

        return results


class PeriodCalcResults:
    CalcName = "Имя модели"
    PeriodName = "Имя периода"
    StartPeriod = "Начало периода"
    EndPeriod = "Конец периода"
    ObjectName = "Имя объекта"
    ParamName = "Имя параметра"
    Unit = "Ед. изм."
    Num = "Доп. Номер"
    Value = "Значение"

    _index = (
        CalcName,
        PeriodName,
        StartPeriod,
        EndPeriod,
        ObjectName,
        ParamName,
        Unit,
        Num,
        Value,
    )

    def __init__(self) -> None:
        self.df = pd.DataFrame(columns=self._index)

    def get_object(self, item: str) -> Optional[PeriodCalcResults]:
        df = self.df[self.df[self.ObjectName] == item]
        if df.empty:
            return None
        new = deepcopy(self)
        new.df = df
        return new

    def get_param(self, item: str) -> Optional[PeriodCalcResults]:
        df = self.df[self.df[self.ParamName] == item]
        if df.empty:
            return None
        new = deepcopy(self)
        new.df = df
        return new

    def append(
        self,
        calc_name: str,
        period_name: Union[pd.Timestamp, str],
        start_period: TimeVector,
        end_period: TimeVector,
        object_name: str,
        param_name: str,
        unit: str,
        num: str,
        value: np.ndarray,
    ):
        df = pd.DataFrame(columns=self._index)
        df[self.Value] = value
        df[self.CalcName] = calc_name
        df[self.PeriodName] = period_name
        df[self.StartPeriod] = start_period
        df[self.EndPeriod] = end_period
        df[self.ObjectName] = object_name
        df[self.ParamName] = param_name
        df[self.Unit] = unit
        df[self.Num] = num

        self.df = pd.concat((self.df, df), ignore_index=True)

    def to_excel(self, name: Union[Path, str]) -> None:
        self.df.to_excel(name)
