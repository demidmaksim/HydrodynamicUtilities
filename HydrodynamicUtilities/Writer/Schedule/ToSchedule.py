from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Optional, Tuple
    from HydrodynamicUtilities.Models.Strategy import ScheduleDataframe as Sdf
    from HydrodynamicUtilities.Models.Time.Vector import TimeVector, TimePoint
    from pathlib import Path

import io
import shutil

from datetime import datetime

from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    WELLTRACK,
)


class SCHDates:
    def __init__(
        self,
        tv: Optional[TimeVector],
        sch_time: Optional[TimeVector],
    ) -> None:
        self.Tv = tv
        self.CurrentTime = None
        self.SchTime = sch_time

    def empty(self) -> bool:
        if self.Tv is not None:
            return self.Tv.shape() == 0
        else:
            return True

    def pop_zero(self) -> str:
        results: TimePoint = self.Tv[0]
        self.Tv = self.Tv[1:]
        self.CurrentTime = results
        return results.to_str(str_format="%d %b %Y %H:%M:%S")

    def predict(self) -> TimePoint:
        return self.Tv[0]

    def check(self, time: TimePoint) -> bool:
        if self.SchTime is None:
            return False
        else:
            return time in self.SchTime


class SCHWriter:
    __Generated_string = f"-- Generated : ScheduleCreator"
    Title = (
        "--ScheduleCreator\n"
        "--Email:   Demid.Maksim@gmail.com\n"
        "--GitHub:  https://github.com/demidmaksim\n"
        "--Created: {t}\n\n\n"
    )
    RelativeReference = ""
    __DesignsKeyword = (WELLTRACK,)

    def __init__(
        self,
        write_none_time_events: bool = False,
        title: str = None,
        compress_dates: bool = True,
        designs_in_separate_files: bool = False,
        relative_reference: str = None
    ) -> None:
        self.WriteNoneTimeEvents = write_none_time_events
        self.CompressDates = compress_dates
        self.DesignsInSeparateFiles = designs_in_separate_files
        if title is not None:
            self.Title = title
        if title is not None:
            self.RelativeReference = relative_reference

    def __added_title(self, to_write: io.StringIO) -> None:
        data = {"t": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        to_write.write(self.Title.format(**data))

    def __write_dates_keyword(
        self,
        time: SCHDates,
        to_write: io.StringIO,
    ) -> None:
        tab = "\t"
        gs = self.__Generated_string
        if not self.CompressDates:
            results = f"DATES{tab * 8}{gs}\n  {time}\t/\n/\n\n"
            to_write.write(results)
        else:
            to_write.write(f"DATES{tab * 8}{gs}\n")
            date = time.pop_zero()
            to_write.write(f"  {date}\t/\n")
            while not time.empty():
                # if time.check(time.predict()):
                #     to_write.write(f"/\n\n")
                #     break
                if time.check(time.CurrentTime):
                    to_write.write(f"/\n\n")
                    break
                date = time.pop_zero()
                to_write.write(f"  {date}\t/\n")
            else:
                to_write.write(f"/\n\n")

    def __write(
        self,
        sdf: Sdf,
        to_write: io.StringIO,
        all_time: Optional[TimeVector],
        event_time: Optional[TimeVector],
    ) -> io.StringIO:

        if all_time is None:
            return to_write

        sch_dates = SCHDates(all_time, event_time)

        while not sch_dates.empty():
            self.__write_dates_keyword(sch_dates, to_write)

            if sch_dates.check(sch_dates.CurrentTime):
                sdf_steps = sdf[sch_dates.CurrentTime.Date]
                for sheet in sdf_steps:
                    to_write = sheet.to_string(to_write)

        return to_write

    @staticmethod
    def __write_none_time(
        sdf: Sdf,
        to_write: io.StringIO,
    ) -> None:
        for sheet in sdf:
            sheet = sheet.get_nan_time()
            if sheet is not None:
                sheet.to_string(to_write)

    @staticmethod
    def get_time(
        all_dates: Optional[TimeVector],
        sdf: Sdf,
    ) -> Tuple[Optional[TimeVector], Optional[TimeVector]]:
        event_dates = sdf.get_dates()
        if all_dates is None:
            all_dates = event_dates
        elif event_dates is not None:
            all_dates.extend(event_dates)
        return all_dates, event_dates

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
        all_dates, event_dates = self.get_time(time, sdf)
        to_write = self.__write(sdf, to_write, all_dates, event_dates)

        with open(path, "w") as file:
            to_write.seek(0)
            shutil.copyfileobj(to_write, file)
