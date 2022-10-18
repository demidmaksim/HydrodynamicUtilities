from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Optional
    from HydrodynamicUtilities.Models.Strategy import ScheduleDataframe as Sdf
    from HydrodynamicUtilities.Models.Strategy import ScheduleSheet as Ss
    from HydrodynamicUtilities.Models.Time.Vector import TimeVector

import io
import shutil

from pathlib import Path

from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    WELLTRACK,
    OneRowKeyword,
)

from datetime import datetime


class SCHWriter:
    __Generated_string = f"-- Generated : ScheduleCreator"

    def __init__(self) -> None:
        self.WriteNoneTimeEvents = False

    @staticmethod
    def __added_title(to_write: io.StringIO) -> None:
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = (
            f"--ScheduleCreator\n"
            f"--Email:   Demid.Maksim@gmail.com\n"
            f"--GitHub:  https://github.com/demidmaksim\n"
            f"--Created: {t}\n\n\n"
        )
        to_write.write(title)

    @classmethod
    def __get_dates_keyword(cls, time: str, to_write: io.StringIO) -> None:
        tab = "\t"
        results = (
            f"DATES{tab * 8}{cls.__Generated_string}\n" f"  {time}\t/\n" f"/\n" f"\n"
        )
        to_write.write(results)

    def __write(
        self,
        sdf: Sdf,
        to_write: io.StringIO,
        time: TimeVector,
    ) -> io.StringIO:
        schedule_time = time.to_eclipse_schedule_list()

        for did, date in enumerate(time.to_datetime64()):
            self.__get_dates_keyword(schedule_time[did], to_write)

            if date in time:
                sdf_steps = sdf[date]
                for sheet in sdf_steps:
                    to_write = sheet.to_string(to_write)
        return to_write

    def __write_none_time(
        self,
        sdf: Sdf,
        to_write: io.StringIO,
    ) -> None:
        for sheet in sdf:
            sheet = sheet.get_nan_time()
            sheet.to_string(to_write)

    def get_time(self, time: Optional[TimeVector], sdf: Sdf) -> TimeVector:
        event_dates = sdf.get_dates()
        if time is None:
            time = event_dates
        else:
            time.extend(event_dates)
        return time

    def drop_none_type(self, sdf: Sdf, to_write: io.StringIO) -> Sdf:
        if self.WriteNoneTimeEvents:
            self.__write_none_time(sdf, to_write)
        return sdf.drop_nan_time(in_place=False)

    def create_schedule(
        self,
        sdf: Sdf,
        time: TimeVector = None,
        path: Union[str, Path] = "Results.sch",
    ) -> None:
        to_write = io.StringIO()
        self.__added_title(to_write)
        sdf = self.drop_none_type(sdf, to_write)
        time = self.get_time(time, sdf)
        to_write = self.__write(sdf, to_write, time)

        with open(path, "w") as file:
            to_write.seek(0)
            shutil.copyfileobj(to_write, file)
