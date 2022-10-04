from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.DataFile import DataFile
    from typing import Any, Union, Optional, List, Type, Iterable, Tuple

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
from ..Base import Keyword, BaseKeywordCreator
import datetime as dt
import numpy as np
import pandas as pd


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
            return np.datetime64("NaT")
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
                if data_file.SCHEDULE.DATES is None:
                    try:
                        date = data_file.RUNSPEC.get_start_date()
                        if date is None:
                            date = np.datetime64("NaT")
                        else:
                            date = date.to_datetime64()
                    except:
                        date = np.datetime64("NaT")
                else:
                    date = data_file.SCHEDULE.DATES.get_last_time()
                if kw != ARITHMETIC.__name__:
                    sr = ScheduleRow(ss.Pattern, [date] + target_data.split())
                else:
                    sr = ScheduleRow(ss.Pattern, [date] + [target_data])

                ss = ss + sr

        return SCHEDULEKeyword(str(kw), ss)

    @staticmethod
    def unknown_keyword(adata: ASCIIText, kw: str) -> Keyword:
        return DirtySchData(kw, str(adata))

    @staticmethod
    def __get_well_bore_name(adata: ASCIIRow) -> Tuple[str, int]:
        data = str(adata).strip()
        if ":" in str(adata):
            ind = data.index(":")
            return data[:ind], int(data[ind:])
        else:
            return str(adata), 0

    def welltrack_keyword(self, adata: ASCIIText) -> Keyword:
        ss = ScheduleSheet(WELLTRACK)
        wdata = adata.get_first_word(True)
        wname, bname = self.__get_well_bore_name(wdata)
        target_data = adata.to_slash(True)
        list_data = target_data.split()
        x = list_data[::4]
        y = list_data[1::4]
        z = list_data[2::4]
        md = list_data[3::4]
        df = pd.DataFrame(columns=WELLTRACK.Order)
        df[WELLTRACK.X] = x
        df[WELLTRACK.Y] = y
        df[WELLTRACK.Z] = z
        df[WELLTRACK.MD] = md
        df[WELLTRACK.WellName] = wname
        df[WELLTRACK.BoreName] = bname
        df[WELLTRACK.PointNumber] = df.index
        ss.DF = df
        return SCHEDULEKeyword(WELLTRACK.__name__, ss)

    def arithmetic(self) -> Keyword:
        pass

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = adata.get_keyword(True)
        adata = adata.replace_multiplication()
        if str(kw).upper() == WELLTRACK.__name__:
            return self.welltrack_keyword(adata)
        elif str(kw).upper() in ScheduleKeyword.keyword.keys():
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
    def get_constructor(cls) -> Type[BaseKeywordCreator]:
        return SCHEDULECreator
