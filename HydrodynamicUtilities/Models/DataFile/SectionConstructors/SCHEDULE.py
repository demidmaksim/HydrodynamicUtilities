from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import Keyword
    from HydrodynamicUtilities.Models.DataFile.DataFile import DataFile
    from typing import Tuple

import numpy as np
import pandas as pd
import datetime as dt

from HydrodynamicUtilities.Models.DataFile.ASCIIFile import ASCIIText, ASCIIRow
from HydrodynamicUtilities.Models.DataFile.Sections import SCHEDULE as SCH

from HydrodynamicUtilities.Models.Strategy.Frame import (
    ScheduleSheet,
    ScheduleRow,
    ScheduleKeyword,
)
from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    ARITHMETIC,
    WELLTRACK,
)

from HydrodynamicUtilities.Reader.ASCIIDataFileReader.BaseCreator import BaseKeywordCreator


class SCHEDULECreator(BaseKeywordCreator):
    @staticmethod
    def data(adata: ASCIIText, kw: str) -> Keyword:
        dates = SCH.DATESkW()
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
    def get_date(data_file: DataFile) -> np.datetime64:
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
        return date

    @classmethod
    def famous_keyword(
        cls,
        adata: ASCIIText,
        kw: str,
        data_file: DataFile,
    ) -> Keyword:
        ss = ScheduleSheet(ScheduleKeyword.keyword[str(kw).upper()])
        while not adata.empty():
            target_data = adata.to_slash(True)
            if not target_data.empty():
                date = cls.get_date(data_file)
                if kw != ARITHMETIC.__name__:
                    sr = ScheduleRow(ss.Pattern, [date] + target_data.split())
                else:
                    sr = ScheduleRow(ss.Pattern, [date] + [target_data])

                ss = ss + sr

        return SCH.SCHEDULEKeyword(str(kw), ss)

    @staticmethod
    def unknown_keyword(adata: ASCIIText, kw: str) -> Keyword:
        return SCH.DirtySchData(kw, str(adata))

    @staticmethod
    def __get_well_bore_name(adata: ASCIIRow) -> Tuple[str, int]:
        data = str(adata).strip()
        data = data.replace("'", "")
        if ":" in str(adata):
            ind = data.index(":")
            return data[:ind], int(data[ind + 1 :])
        else:
            return str(data), 0

    def welltrack_keyword(self, adata: ASCIIText, data_file: DataFile) -> Keyword:
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
        df["Time"] = self.get_date(data_file)
        ss.DF = df
        return SCH.SCHEDULEKeyword(WELLTRACK.__name__, ss)

    def arithmetic(self) -> Keyword:
        pass

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = adata.get_keyword(True)
        adata = adata.replace_multiplication()
        if str(kw).upper() == WELLTRACK.__name__:
            return self.welltrack_keyword(adata, data_file)
        elif str(kw).upper() in ScheduleKeyword.keyword.keys():
            return self.famous_keyword(adata, str(kw), data_file)
        elif str(kw) == "DATES":
            return self.data(adata, str())
        else:
            return self.unknown_keyword(adata, str(kw))
