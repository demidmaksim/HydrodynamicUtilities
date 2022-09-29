from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from typing import Dict, List, Type, Any, Iterator, Tuple, Optional, Union, Iterable


import pandas as pd

from copy import deepcopy

from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    ScheduleKeyword,
    BaseKeyWord,
)
from HydrodynamicUtilities.Models.Time.Vector import TimeVector


class ScheduleRow:
    def __init__(self, pattern: Type[BaseKeyWord], data: Iterable = None) -> None:
        self.Pattern = pattern
        self.DF = pd.Series(index=("Time",) + pattern.Order, dtype=object)
        if data is not None:
            for v_id, value in enumerate(data):
                if v_id < len(self.DF.values):
                    if value != "1*":
                        self.DF.iloc[v_id] = value
                else:
                    print("redundant value")

    def __repr__(self) -> str:
        return f"ScheduleRow: {self.Pattern.__name__}"

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("Pattern", "DF"):
            return super().__setattr__(key, value)

        if key in super().__getattribute__("Pattern").Order:
            name = key
        elif key != "Time":
            name = getattr(self.Pattern, key)
        else:
            name = "Time"

        self.DF[name] = value

    def __getattr__(self, item: str) -> Any:
        if item in ("Pattern", "DF"):
            return super().__getattribute__(item)

        if item != "Time" and item not in self.Pattern.Order:
            name = getattr(self.Pattern, item)
        elif item == "Time":
            name = "Time"
        else:
            name = item

        return self.DF[name]

    def __getitem__(
        self,
        item: Union[np.datetime64, np.ndarray],
    ) -> Optional[ScheduleRow]:
        new = deepcopy(self)
        if type(item) == np.datetime64:
            pattern = self.DF["Time"].values == item
            new.DF = self.DF[pattern]
        elif type(item) == np.ndarray:
            if type(item[0]) == np.datetime64:
                pattern = np.zeros(self.DF["Time"].values.shape)
                pattern = pattern.astype(bool)
                for point in item:
                    pattern = pattern | (self.DF["Time"].values == point)
                    new.DF = self.DF[pattern]
            elif type(item[0]) == int:
                pattern = item
                new.DF = self.DF.iloc[pattern, :]
            elif type(item[0]) in (bool, np.bool8, np.bool_):
                pattern = item
                new.DF = self.DF[pattern]
        else:
            raise TypeError

        if not new.DF.empty:
            return new
        else:
            return None

    def __setitem__(self, key: Any, value: Any) -> None:
        self.DF[key] = value

    def __iter__(self) -> Iterator[Tuple[str, np.ndarray]]:
        results = []
        for key in ("Time",) + self.Pattern.Order:
            try:
                value = getattr(self, key)
                results.append((key, value))
            except AttributeError:
                results.append((key, None))
        return iter(results)

    def empty(self) -> bool:
        return all(pd.isna(self.DF.values))


class ScheduleSheet:
    def __init__(self, pattern: Type[BaseKeyWord]):
        self.Pattern = pattern
        self.DF = pd.DataFrame(columns=("Time",) + pattern.Order)

    def __repr__(self) -> str:
        return f"ScheduleSheet: {self.Pattern.__name__}"

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("Pattern", "DF"):
            return super().__setattr__(key, value)

        if key in super().__getattribute__("Pattern").Order:
            name = key
        elif key != "Time":
            name = getattr(self.Pattern, key)
        else:
            name = "Time"

        self.DF[name] = value

    def __getattr__(self, item: str) -> Any:
        if item in ("Pattern", "DF"):
            return super().__getattribute__(item)

        if item != "Time" and item not in self.Pattern.Order:
            name = getattr(self.Pattern, item)
        elif item == "Time":
            name = "Time"
        else:
            name = item

        return self.DF[name]

    def __getitem__(
        self,
        item: Union[np.datetime64, np.ndarray],
    ) -> Optional[ScheduleSheet]:
        new = deepcopy(self)
        if type(item) == np.datetime64:
            pattern = self.DF["Time"].values == item
            new.DF = self.DF[pattern]
        elif type(item) == np.ndarray:
            if type(item[0]) == np.datetime64:
                pattern = np.zeros(self.DF["Time"].values.shape)
                pattern = pattern.astype(bool)
                for point in item:
                    pattern = pattern | (self.DF["Time"].values == point)
                    new.DF = self.DF[pattern]
            elif type(item[0]) == int:
                pattern = item
                new.DF = self.DF.iloc[pattern, :]
            elif type(item[0]) in (bool, np.bool8, np.bool_):
                pattern = item
                new.DF = self.DF[pattern]
        else:
            raise TypeError

        if not new.DF.empty:
            return new
        else:
            return None

    def __iter__(self) -> Iterator[Tuple[str, np.ndarray]]:
        results = []
        for key in ("Time",) + self.Pattern.Order:
            try:
                value = getattr(self, key)
                results.append((key, value))
            except AttributeError:
                results.append((key, None))
        return iter(results)

    def __add__(self, other: Union[ScheduleSheet, ScheduleRow]) -> ScheduleSheet:
        if other is None:
            return self

        if self.Pattern != other.Pattern:
            raise TypeError

        new = deepcopy(self)

        new.DF = pd.concat([new.DF, other.DF], ignore_index=True)

        return new

    def iter_row(self) -> Iterator[Tuple[int, pd.Series]]:
        for irow, row in self.DF.iterrows():
            yield irow, row

    def loc(self, column_name: str) -> pd.Series:
        return self.DF[column_name]

    def check_duplicated(self) -> pd.Series:
        pass

    def get_time(
        self,
        unique: bool = True,
        sort: bool = True,
    ) -> Optional[TimeVector]:
        time_series = self.Time

        if time_series.empty:
            return None

        time = TimeVector(time_series)

        if unique:
            time.unique(in_place=True)

        if sort:
            time.sort(in_place=True)

        return time

    def to_dataframe(self) -> pd.DataFrame:
        new = deepcopy(self.DF)
        return new

    def drop_nan_time(self, in_place: bool = True) -> Optional[ScheduleSheet]:
        pattern = pd.isna(self.DF["Time"])
        new_df = self.DF[~pattern]
        if in_place:
            self.DF = new_df
            return None
        else:
            new = deepcopy(self)
            new.DF = new_df
            return new

    def drop_not_nan_time(self, in_place: bool = True) -> Optional[ScheduleSheet]:
        pattern = pd.isna(self.DF["Time"])
        new_df = self.DF[pattern]
        if in_place:
            self.DF = new_df
            return None
        else:
            new = deepcopy(self)
            new.DF = new_df
            return new

    def empty(self) -> bool:
        return self.DF.empty

    def add_row(self, data: ScheduleRow) -> None:
        self.DF.loc[len(self.DF)] = data.DF


class ScheduleDataframe:
    def __init__(
        self,
        data: Union[
            Dict[str, pd.DataFrame],
            Dict[str, ScheduleSheet],
        ] = None,
    ) -> None:
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)

    def __setattr__(
        self,
        key: str,
        value: Union[ScheduleSheet, pd.DataFrame],
    ) -> None:
        if key not in ScheduleKeyword.keyword.keys():
            raise AttributeError
        if type(value) == ScheduleSheet:
            if key != value.Pattern.__name__:
                raise AttributeError("Keyword != Keyword.Name")
        elif type(value) == pd.DataFrame:
            # TODO
            pass
        else:
            raise TypeError

        super().__setattr__(key, value)

    def __getattr__(self, item: str) -> ScheduleSheet:
        if item not in ScheduleKeyword.keyword.keys():
            raise AttributeError
        results: ScheduleSheet = super().__getattribute__(item)
        return results

    def __iter__(self) -> Iterator[ScheduleSheet]:
        keys = self.keys()
        results = []
        for key in keys:
            results.append(getattr(self, key))
        return iter(results)

    def __getitem__(self, key: Any) -> ScheduleDataframe:
        new = deepcopy(self)
        for keyword in self:
            value = keyword[key]
            if value is not None:
                setattr(new, keyword.Pattern.__name__, value)
            else:
                delattr(new, keyword.Pattern.__name__)
        return new

    def __contains__(self, item: Type[BaseKeyWord]) -> bool:
        return item.__name__ in self.keys()

    def __add__(
        self,
        other: Union[ScheduleDataframe, ScheduleSheet, None],
    ) -> ScheduleDataframe:

        new = deepcopy(self)

        if type(other) == ScheduleDataframe:
            for sheet in other:
                name = sheet.Pattern.__name__
                try:
                    self_sheet = getattr(self, name)
                    setattr(new, name, self_sheet + sheet)
                except AttributeError:
                    setattr(new, name, sheet)
            return new

        elif type(other) == ScheduleSheet:
            name = other.Pattern.__name__
            try:
                self_sheet = getattr(self, name)
                setattr(new, name, self_sheet + other)
            except AttributeError:
                setattr(new, name, other)
            return new

        elif isinstance(other, type(None)):
            return deepcopy(self)
        else:
            raise TypeError

    def __iadd__(self, other: Union[ScheduleDataframe, ScheduleSheet]) -> None:
        if type(other) == ScheduleDataframe:
            for sheet in other:
                name = sheet.Pattern.__name__
                try:
                    self_sheet = getattr(self, name)
                    setattr(self, name, self_sheet + sheet)
                except AttributeError:
                    setattr(self, name, sheet)

        elif type(other) == ScheduleSheet:
            name = other.Pattern.__name__
            try:
                self_sheet = getattr(self, name)
                setattr(self, name, self_sheet + other)
            except AttributeError:
                setattr(self, name, other)

        else:
            raise TypeError

    def keys(self) -> List[str]:
        # TODO rework
        results = []
        for key in ScheduleKeyword.Order:
            if hasattr(self, key.__name__):
                results.append(key.__name__)
        return results

    def get_dates(
        self,
        unique: bool = True,
        sort: bool = True,
    ) -> Optional[TimeVector]:
        time = None
        for keyword in self:
            if time is None:
                sheet_time = keyword.get_time(unique=False, sort=False)
                if sheet_time is not None:
                    time = sheet_time
            else:
                sheet_time = keyword.get_time(unique=False, sort=False)
                if sheet_time is not None:
                    time.extend(sheet_time)

        if unique and time is not None:
            time.unique(in_place=True)

        if sort and time is not None:
            time.sort(in_place=True)

        return time

    def drop_nan_time(
        self,
        in_place: bool = True,
    ) -> Optional[ScheduleDataframe]:

        if in_place:
            for keyword in self:
                keyword.drop_nan_time()
            return None
        else:
            new = deepcopy(self)
            for keyword in new:
                new_sheet = keyword.drop_nan_time(in_place=False)
                setattr(new, keyword.Pattern.__name__, new_sheet)
            return new

    def drop_not_nan_time(
        self,
        in_place: bool = True,
    ) -> Optional[ScheduleDataframe]:
        if in_place:
            for keyword in self:
                keyword.drop_not_nan_time()
            return None
        else:
            new = deepcopy(self)
            for keyword in new:
                new_sheet = keyword.drop_not_nan_time(in_place=False)
                setattr(new, keyword.Pattern.__name__, new_sheet)
            return new

    def empty(self) -> bool:
        for sheet in self.__iter__():
            if not sheet.empty():
                return False
        return True

    def add_row(self, data: ScheduleRow) -> None:
        if self.__contains__(data.Pattern):
            sheet = self.__getattr__(data.Pattern.__name__)
        else:
            sheet = ScheduleSheet(data.Pattern)
            self.__setattr__(sheet.Pattern.__name__, sheet)
        sheet.add_row(data)
