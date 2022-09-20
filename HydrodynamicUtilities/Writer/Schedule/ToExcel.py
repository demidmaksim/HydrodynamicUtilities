from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.Strategy.Frame import (
        ScheduleSheet,
        ScheduleDataframe,
    )

import xlsxwriter as xlsw
import pandas as pd

from pathlib import Path
from copy import deepcopy

from HydrodynamicUtilities.Models.Source.EclipseScheduleNames import ScheduleKeyword


def __from_schedule_sheet(
    ss: ScheduleSheet,
    workbook: xlsw.workbook = None,
) -> None:
    sheet = workbook.add_worksheet(ss.Pattern.__name__)
    sheet.nan_inf_to_errors = True
    cell_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "center_across": True,
            "valign": "vcenter",
            "fg_color": "#D7E4BC",
            "border": 1,
        }
    )

    date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})

    sheet.write_row(0, 0, ("Time",) + ss.Pattern.Order, cell_format)

    for kid, key in enumerate(("Time",) + ss.Pattern.Order):
        if key == "Time":
            for pid, point in enumerate(ss.get_time(False, False).to_datetime_list()):
                if point is not None:
                    sheet.write_datetime(1 + pid, kid, point, date_format)
        else:
            # try:
            value = getattr(ss, key)
            copy_value = deepcopy(value)
            copy_value[pd.isna(value).values] = ""
            sheet.write_column(1, kid, copy_value)
            # except AttributeError:
            #     pass


def write_xlsx(sdf: ScheduleDataframe, link: Path = Path("Schedule.xlsx")) -> None:
    workbook = xlsw.Workbook(link)

    for keyword in sdf:
        __from_schedule_sheet(keyword, workbook)

    workbook.close()


def get_pattern(link: Path = Path("Template.xlsx")) -> None:

    workbook = xlsw.Workbook(link)

    cell_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "center_across": True,
            "valign": "vcenter",
            "fg_color": "#D7E4BC",
            "border": 1,
        }
    )

    for keyword in ScheduleKeyword.ForWrite:
        sheet = workbook.add_worksheet(keyword.__name__)
        sheet.write_row(0, 0, ("Time",) + keyword.Order, cell_format)

    workbook.close()
