from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Optional, Tuple, Dict
    from HydrodynamicUtilities.Models.Strategy import ScheduleDataframe as Sdf
    from HydrodynamicUtilities.Models.Strategy import ScheduleSheet as Ss
    from HydrodynamicUtilities.Models.Time.Vector import TimeVector


import io
import os
import shutil
import pandas as pd

from pathlib import Path
from datetime import datetime

from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    WELLTRACK,
)
from HydrodynamicUtilities.Models.Time import TimePoint


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
    RelativeReference = "SCHEDULE"
    __DesignsKeyword = (WELLTRACK,)
    GroupDesignsName = "WELLTRACK/{name_model}"

    def __init__(
        self,
        write_none_time_events: bool = False,
        title: str = None,
        compress_dates: bool = True,
        designs_in_separate_files: bool = False,
        group_designs: bool = True,
        relative_reference: str = None,
    ) -> None:
        self.WriteNoneTimeEvents = write_none_time_events
        self.CompressDates = compress_dates
        self.DesignsInSeparateFiles = designs_in_separate_files
        self.GroupDesigns = group_designs
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

    def __write_well_track_file(self, sdf: Sdf, target_path: Path) -> Dict[str, str]:

        if not self.DesignsInSeparateFiles:
            return dict()

        if self.GroupDesigns:
            filename, file_extension = os.path.splitext(target_path.name)
            new_folder = self.GroupDesignsName.format(name_model=filename)
            path = target_path.parent / self.RelativeReference / new_folder
            os.makedirs(path, exist_ok=True)
        else:
            path = Path("")

        results = dict()
        df = sdf.WELLTRACK.DF
        for wname in pd.unique(df[WELLTRACK.WellName]):
            wdf = df[df[WELLTRACK.WellName] == wname]
            welltrack_file = io.StringIO()
            number = len(pd.unique(wdf["Time"]))
            for tstep in pd.unique(wdf["Time"]):
                tdf = df[df["Time"] == tstep]
                welltrack_file = WELLTRACK.to_string(tdf, welltrack_file)
                t = TimePoint(tstep).to_str("%Y_%m_%d_%H_%M_%S")
                if number > 1:
                    name_file = f"{wname}_{t}.trj"
                else:
                    name_file = f"{wname}.trj"

                results[f"{wname}_{t}"] = str(path / name_file)
                with open(path / name_file, "w") as file:
                    welltrack_file.seek(0)
                    shutil.copyfileobj(welltrack_file, file)
        return results

    def __write_welltrack_dict(
        self, to_write: io.StringIO, sheet: Ss, time: TimePoint, wtdict: Dict[str, str]
    ) -> io.StringIO:
        str_time = time.to_str("%Y_%m_%d_%H_%M_%S")
        for wname in pd.unique(sheet.DF[WELLTRACK.WellName]):
            path = wtdict[f"{wname}_{str_time}"]
            to_write.write(f"INCLUDE\t '{path}'\t/\n")
        to_write.write("\n")
        return to_write

    def __write(
        self,
        sdf: Sdf,
        to_write: io.StringIO,
        all_time: Optional[TimeVector],
        event_time: Optional[TimeVector],
        target_path: Path,
    ) -> io.StringIO:

        if all_time is None:
            return to_write

        sch_dates = SCHDates(all_time, event_time)

        welltrack_file = self.__write_well_track_file(sdf, target_path)

        while not sch_dates.empty():
            self.__write_dates_keyword(sch_dates, to_write)

            if sch_dates.check(sch_dates.CurrentTime):
                sdf_steps = sdf[sch_dates.CurrentTime.Date]
                for sheet in sdf_steps:
                    if not issubclass(sheet.Pattern, WELLTRACK):
                        to_write = sheet.to_string(to_write)
                    elif self.DesignsInSeparateFiles:
                        to_write = self.__write_welltrack_dict(
                            to_write,
                            sheet,
                            TimePoint(sch_dates.CurrentTime.Date),
                            welltrack_file,
                        )
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
        if isinstance(path, str):
            path = Path(path)

        to_write = io.StringIO()
        self.__added_title(to_write)
        sdf = self.drop_none_type(sdf, to_write)
        all_dates, event_dates = self.get_time(time, sdf)
        to_write = self.__write(sdf, to_write, all_dates, event_dates, path)

        with open(path, "w") as file:
            to_write.seek(0)
            shutil.copyfileobj(to_write, file)
