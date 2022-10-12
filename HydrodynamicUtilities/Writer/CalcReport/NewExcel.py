from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Tuple

from typing import Iterable

import xlsxwriter as xlsw
from HydrodynamicUtilities.Models.EclipseBinaryFile import SUMMARY
from HydrodynamicUtilities.Models.ParamVector import Interpolation, CumTimeSeriasParam
from HydrodynamicUtilities.Models.Time import TimeVector, generate_time_vector

from .ExcelFormula import formula

import pandas as pd
import numpy as np
from copy import deepcopy


class ReportData:
    def __init__(
        self,
        well_names: List[str],
        group_names: List[str],
        calc_names: List[str],
    ) -> None:
        self.WellNames = well_names
        self.GroupNames = group_names
        self.CalcNames = calc_names


def get_report_data(summary: Iterable[SUMMARY]) -> ReportData:
    well_names = []
    group_names = []
    calc_names = []
    for su in summary:
        well_names.append(su.CalcName)
        well_names.append(su.get_well_names())
        well_names.append(su.get_group_name())
    return ReportData(
        pd.unique(well_names),
        pd.unique(group_names),
        pd.unique(calc_names),
    )


def create(summary: Iterable[SUMMARY]) -> None:
    setting = get_report_data(summary)

