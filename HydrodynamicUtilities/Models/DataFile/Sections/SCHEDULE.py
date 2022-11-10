from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.DataFile import DataFile
    from typing import Any, Union, Optional, List, Type, Iterable, Tuple, Dict

from typing import Iterable
from ..Base import Section, UnknownKeyword

from HydrodynamicUtilities.Models.Time import TimePoint
from HydrodynamicUtilities.Models.Strategy.Frame import (
    ScheduleDataframe,
    ScheduleSheet,
    ScheduleRow,
)
from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    ScheduleKeyword,
    WELLTRACK,
    ARITHMETIC,
)
from ..ASCIIFile import ASCIIText, ASCIIRow
from ..Base import Keyword
import datetime as dt
import numpy as np
import pandas as pd


class DirtySchData(UnknownKeyword):
    def __init__(self, keyword_name: str, data: str) -> None:
        super().__init__(keyword_name, data)

    def __repr__(self) -> str:
        return self.Name


class SCHEDULEKeyword(Keyword):
    def __init__(self, kw: str, data: ScheduleSheet, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ScheduleSheet = data
        self.Name = kw


class DATESkW(Keyword):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Dates = []

    def __add__(self, other: DATESkW) -> None:
        if not isinstance(other, DATESkW):
            raise TypeError
        self.extend(other.Dates)

    def append(self, value: Union[np.datetime64, TimePoint]) -> None:
        if isinstance(value, TimePoint):
            value = value.to_datetime64()
        self.Dates.append(value)

    def extend(
        self, values: Union[Iterable[Union[np.datetime64, TimePoint]], DATESkW]
    ) -> None:
        if isinstance(values, Iterable):
            for value in values:
                self.append(value)
        elif isinstance(values, DATESkW):
            self.extend(values.Dates)
        else:
            raise TypeError

    def get_last_time(self) -> np.datetime64:
        if not self.Dates:
            return np.datetime64("NaT")
        else:
            return self.Dates[-1]


class SCHEDULE(Section):
    def __init__(self, data_file: DataFile) -> None:
        super().__init__(data_file)
        self.SDF = ScheduleDataframe()
        self.DirtyData = []
        self.DATES: Optional[DATESkW] = None

    def __setattr__(self, key: str, value: Any) -> None:

        if isinstance(value, ScheduleDataframe):
            if hasattr(self, key):
                self.SDF.append(value)
            else:
                super(SCHEDULE, self).__setattr__(key, value)

        elif isinstance(value, ScheduleSheet):
            self.SDF.append(value)

        elif isinstance(value, SCHEDULEKeyword):
            self.SDF.append(value.ScheduleSheet)

        elif isinstance(value, DirtySchData):
            self.DirtyData.append(value)

        elif isinstance(value, DATESkW):

            if self.DATES is None:
                super().__setattr__(key, value)
            else:
                self.DATES.extend(value)

        elif key in ("_Section__DataFile", "SDF", "DirtyData", "Dates"):
            super(SCHEDULE, self).__setattr__(key, value)

        else:
            super().__setattr__(key, value)

    @classmethod
    def get_famous_keywords(cls) -> Dict[str, Type[Keyword]]:
        return ScheduleKeyword.keyword
