from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union
    from HydrodynamicUtilities.Models.Strategy import (
        ScheduleSheet,
        ScheduleDataframe,
    )
    from HydrodynamicUtilities.Models.Time.Vector import TimeVector

import io
import shutil
import pandas as pd

from pathlib import Path
from tabulate import tabulate

from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import (
    WELLTRACK,
    ARITHMETIC,
    OneRowKeyword,
)

from datetime import datetime


Generated_string = f"-- Generated : ScheduleCreator"


def __added_title(to_write: io.StringIO) -> None:
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = (
        f"--ScheduleCreator\n"
        f"--Email:   Demid.Maksim@gmail.com\n"
        f"--GitHub:  https://github.com/demidmaksim\n"
        f"--Created: {t}\n\n\n"
    )

    to_write.write(title)


def __get_dates_keyword(time: str, to_write: io.StringIO) -> None:
    results = f"DATES" + "\t" * 8 + Generated_string + f"\n  {time}\t/\n/\n\n"
    to_write.write(results)


def __one_row_keyword(
    ss: ScheduleSheet,
    to_write: io.StringIO,
) -> None:

    df = ss.DF.drop("Time", axis=1)

    if not df.empty:
        to_write.write(f"{ss.Pattern.__name__}\n")
        if type(ss.Pattern) != ARITHMETIC:
            df["End"] = "/"

        new_df = df.fillna(value="1*")
        for_write = tabulate(new_df, showindex=False, tablefmt="plain")
        to_write.write("  ")
        to_write.write(for_write.replace("\n", "\n  "))

        to_write.write(f"\n/\n\n")


def __commit_keyword(
    ss: ScheduleSheet,
    to_write: io.StringIO,
) -> None:
    df = ss.DF.drop("Time", axis=1)

    if not df.empty:
        # to_write.write(f"{ss.Pattern.__name__}\n")
        # if type(ss.Pattern) != ARITHMETIC:
        #     df["End"] = "/"

        new_df = df.fillna(value=" ")
        for_write = tabulate(new_df, showindex=False, tablefmt="plain")
        to_write.write("  ")
        to_write.write(for_write.replace("\n", "\n--"))

        to_write.write(f"\n")


def __arbitrary_word(
    ss: ScheduleSheet,
    to_write: io.StringIO,
) -> None:

    df = ss.DF.drop("Time", axis=1)

    if not df.empty:
        to_write.write(f"{ss.Pattern.__name__}\n")
        if type(ss.Pattern) != ARITHMETIC:
            df["End"] = "/"

        new_df = df.fillna(value="1*")
        for_write = tabulate(new_df, showindex=False, tablefmt="plain")
        to_write.write("  ")
        to_write.write(for_write.replace("\n", "\n  "))

        to_write.write(f"\n/\n\n")


def __write_welltrack(
    ss: ScheduleSheet,
    to_write: io.StringIO,
) -> None:
    df = ss.DF.drop("Time", axis=1)
    for wname in pd.unique(df[WELLTRACK.WellName]):
        well_df = df[df[WELLTRACK.WellName] == wname]
        for bname in pd.unique(well_df[WELLTRACK.BoreName]):
            bore_df = well_df[well_df[WELLTRACK.BoreName] == bname]
            bore_df = bore_df.sort_values(WELLTRACK.PointNumber)
            bore_df = bore_df.drop(WELLTRACK.WellName, axis=1)
            bore_df = bore_df.drop(WELLTRACK.BoreName, axis=1)
            bore_df = bore_df.drop(WELLTRACK.PointNumber, axis=1)

            if int(bname) == 0:
                to_write.write(f"WELLTRACK {wname}\n")
            else:
                to_write.write(f"WELLTRACK {wname}:{bname}\n")
            bore_df = bore_df.astype(float)
            bore_df = bore_df.fillna(value="1*")
            for_write = tabulate(
                bore_df, showindex=False, tablefmt="plain", floatfmt=".2f"
            )
            to_write.write("  ")
            to_write.write(for_write.replace("\n", "\n  "))
            to_write.write(f"\n/\n\n")


def __write(
    sdf: ScheduleDataframe,
    event_dates: TimeVector,
    to_write: io.StringIO,
    time: TimeVector = None,
) -> io.StringIO:
    if time is not None:
        schedule_time = time.to_eclipse_schedule_list()
    else:
        schedule_time = event_dates.to_eclipse_schedule_list()
        time = event_dates

    for did, date in enumerate(time.to_datetime64()):
        __get_dates_keyword(schedule_time[did], to_write)

        if date in event_dates:
            sdf_steps = sdf[date]
            for sheet in sdf_steps:

                if issubclass(sheet.Pattern, OneRowKeyword):
                    __one_row_keyword(sheet, to_write)

                if issubclass(sheet.Pattern, WELLTRACK):
                    __write_welltrack(sheet, to_write)

    return to_write


def __write_none_time(sdf: ScheduleDataframe, to_write: io.StringIO) -> None:
    for sheet in sdf:

        if issubclass(sheet.Pattern, OneRowKeyword):
            __one_row_keyword(sheet, to_write)

        if issubclass(sheet.Pattern, WELLTRACK):
            __write_welltrack(sheet, to_write)


def create_schedule(
    sdf: ScheduleDataframe,
    time: TimeVector = None,
    path: Union[str, Path] = "Results.sch",
    empty_dates: bool = False,
) -> None:
    to_write = io.StringIO()
    __added_title(to_write)

    if empty_dates:
        __write_none_time(sdf, to_write)

    sdf = sdf.drop_nan_time(in_place=False)
    # strategy = __forced_conversion(strategy)

    event_dates = sdf.get_dates()
    if time is None:
        time = event_dates
    else:
        time.extend(event_dates)

    if time is not None:
        time = time.unique()
        to_write = __write(sdf, event_dates, to_write, time)

    with open(path, "w") as file:
        to_write.seek(0)
        shutil.copyfileobj(to_write, file)
