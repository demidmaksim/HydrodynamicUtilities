from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.DataFile import DataFile
    from typing import Any, Union, Optional, List, Type, Iterable


from ..Base import Section, UnknownKeyword

from HydrodynamicUtilities.Models.Time import TimePoint
from HydrodynamicUtilities.Models.Strategy.Frame import (
    ScheduleDataframe,
    ScheduleSheet,
    ScheduleRow,
)
from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import ScheduleKeyword
from HydrodynamicUtilities.Models.Source.EtNKW_crutch import data as all_ecl_keyword
from ..ASCIIFile import ASCIIText, ASCIIRow
from ..Base import Keyword, BaseKeywordCreator
import datetime as dt
import numpy as np


class DirtySchData(UnknownKeyword):
    def __init__(self, keyword_name: str, data: str) -> None:
        super().__init__(keyword_name, data)

    def __repr__(self) -> str:
        return self.Name


class SCHEDULEKeyword(Keyword):
    def __init__(self, kw: str, data: ScheduleSheet) -> None:
        self.ScheduleSheet = data
        self.Name = kw


class DATESkW(Keyword):
    def __init__(self) -> None:
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
            return np.NAN
        else:
            return self.Dates[-1]


class SCHEDULECreator(BaseKeywordCreator):
    @staticmethod
    def data(adata: ASCIIText, kw: str) -> Keyword:
        dates = DATESkW()
        while not adata.empty():
            target_data = adata.to_slash(True)
            if not target_data.empty():
                d = str(target_data)
                try:
                    pdt = dt.datetime.strptime(d, "%d %b %Y")
                except ValueError:
                    try:
                        pdt = dt.datetime.strptime(d, "%d %b %Y %H:%M:%S")
                    except ValueError:
                        try:
                            pdt = dt.datetime.strptime(d, "%d %b %Y %H")
                        except ValueError:
                            pdt = dt.datetime.strptime(d, "%d %b %Y %H:%M")

                dt64 = np.datetime64(pdt.strftime("%Y-%m-%d %H:%M:%S"))
                dates.append(dt64)
        return dates

    @staticmethod
    def famous_keyword(
        adata: ASCIIText,
        kw: str,
        data_file: DataFile,
    ) -> Keyword:
        ss = ScheduleSheet(ScheduleKeyword.keyword[str(kw).upper()])
        while not adata.empty():
            target_data = adata.to_slash(True)
            if not target_data.empty():
                if data_file.SCHEDULE.Dates is None:
                    try:
                        date = data_file.RUNSPEC.get_start_date()
                        if date is None:
                            date = np.NAN
                        else:
                            date = date.to_datetime64()
                    except:
                        date = np.NAN
                else:
                    date = data_file.SCHEDULE.Dates.get_last_time()
                sr = ScheduleRow(ss.Pattern, [date] + target_data.split())
                ss = ss + sr

        return SCHEDULEKeyword(str(kw), ss)

    @staticmethod
    def unknown_keyword(adata: ASCIIText, kw: str) -> Keyword:
        return DirtySchData(kw, str(adata))

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = adata.get_keyword(True)
        adata = adata.replace_multiplication()
        if str(kw).upper() in ScheduleKeyword.keyword.keys():
            return self.famous_keyword(adata, str(kw), data_file)
        elif str(kw) == "DATES":
            return self.data(adata, str())
        else:
            return self.unknown_keyword(adata, str(kw))


class SCHEDULE(Section):
    def __init__(self, data_file: DataFile) -> None:
        super().__init__(data_file)
        self.SDF = ScheduleDataframe()
        self.DirtyData = []
        self.Dates: Optional[DATESkW] = None

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
            if self.Dates is None:
                super(SCHEDULE, self).__setattr__(key, value)
            else:
                self.Dates.extend(value)

        elif key in ("_Section__DataFile", "SDF", "DirtyData", "Dates"):
            super(SCHEDULE, self).__setattr__(key, value)

        else:
            raise TypeError

    @classmethod
    def get_constructor(cls) -> Type[BaseKeywordCreator]:
        return SCHEDULECreator
