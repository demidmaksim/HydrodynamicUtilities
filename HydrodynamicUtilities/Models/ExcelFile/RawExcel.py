from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Union, Iterator, Tuple, Type, Optional

import os
import re
import pandas as pd
import numpy as np
import datetime as dt

from pathlib import Path

from .Converters.Converters import ConvertorToRateWellData
from ..HistoryData import (
    WellMeasurement,
    WellHistory,
    FieldHistory,
    ConstructionHistory,
    VFPHistory,
    ValesController,
)
from ..Time import TimeVector, TimeDelta, TimePoint
from ..Strategy import ScheduleDataframe, ScheduleSheet, Strategy
from ..Source.EclipseScheduleNames import BaseKeyWord, ScheduleKeyword
from ..ParamVector import TimeSeries


def excel_time_to_time_vector(etime: np.ndarray) -> TimeVector:
    if etime.shape[0] == 0:
        raise ValueError

    tid = 0
    for tid, t in enumerate(etime):
        if not pd.isna(t):
            break

    if isinstance(etime[tid], float) or isinstance(etime[0], int):
        td = TimeDelta(etime)
        return td + TimePoint("1899-12-30")
    elif type(etime[tid]) == np.datetime64:
        return TimeVector(etime)
    elif type(etime[tid]) == dt.datetime:
        return TimeVector(list(etime))
    else:
        raise TypeError


def convert_to_history_format(df: pd.DataFrame) -> pd.DataFrame:
    first_level = df.iloc[0].fillna(method="ffill").values
    second_level = df.iloc[1].values
    cdf = pd.DataFrame()
    cdf["first_level"] = first_level
    cdf["second_level"] = second_level
    cdf = cdf.astype(str)
    while any(cdf.duplicated()):
        value = cdf.loc[cdf.duplicated(), "second_level"] + "\\d"
        cdf.loc[cdf.duplicated(), "second_level"] = value

    columns = [cdf["first_level"].values, cdf["second_level"].values]
    values = df.values[3:, :]
    return pd.DataFrame(data=values, columns=columns)


def convert_to_schedule_sheet_format(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=df.iloc[0]).drop(df.index[0])


def remove_unnecessary(
    df: pd.DataFrame,
    keyword_pattern: Type[BaseKeyWord],
) -> Optional[pd.DataFrame]:

    if df.empty:
        return None

    df = convert_to_schedule_sheet_format(df)

    if df.empty:
        return None

    new = pd.DataFrame()

    if "Дата" in df.columns:
        values = excel_time_to_time_vector(df["Дата"].values)
        new["Time"] = values.to_datetime64()
    else:
        values = excel_time_to_time_vector(df["Time"].values)
        new["Time"] = values.to_datetime64()

    # new["Time"] = new["Time"].astype(dtype="datetime64[s]")

    for column in keyword_pattern.Order:
        new[column] = df[column].values

    new = new.dropna(how="all")

    return new


class RawExcelSheet:
    def __init__(self, df: pd.DataFrame, name: str) -> None:
        self.DF = df
        self.Name = name

    def __repr__(self) -> str:
        return f"Sheet: {self.Name}"

    def get_well_measurement(
        self,
        time_name: Tuple[str, ...] = ("Время", "Общее"),
        binding: Dict[str, Tuple[str, ...]] = None,
    ) -> WellMeasurement:
        sheet = self.DF
        sheet = sheet.dropna(how="all")
        df = convert_to_history_format(sheet)
        # df = df.iloc[1:, :]
        tserias = df
        for col in time_name:
            tserias = tserias[col]
        tv = excel_time_to_time_vector(tserias.values)
        return ConvertorToRateWellData().convert(df, tv)

    def get_events(self, keyword_name: str) -> ScheduleSheet:
        template = ScheduleKeyword()[keyword_name]
        df = remove_unnecessary(self.DF, template)
        if df is not None:
            sheet = ScheduleSheet(template)
            sheet.DF = df
            return sheet
        else:
            return ScheduleSheet(template)

    def __get_time(
        self,
        sheet: pd.DataFrame,
        time_name: Tuple[str, ...] = ("Время", "Общее"),
    ) -> TimeVector:
        for col in time_name:
            sheet = sheet[col]
        return excel_time_to_time_vector(sheet.values)

    def __get_vfp_history(
        self,
        vfp_column_name: str,
        time_name: Tuple[str, ...] = ("Время", "Общее"),
    ) -> VFPHistory:
        sheet = self.DF
        sheet = sheet.dropna(how="all")
        sheet = convert_to_history_format(sheet)
        serias = sheet[vfp_column_name]
        tv = self.__get_time(sheet, time_name)
        data = TimeSeries(tv, serias.values.T[0])
        return VFPHistory(data)

    def __get_valve(
        self,
        valve_size_column_nam: str,
        time_name: Tuple[str, ...] = ("Время", "Общее"),
    ) -> ValesController:
        results = ValesController()
        sheet = self.DF
        sheet = sheet.dropna(how="all")
        sheet = convert_to_history_format(sheet)
        if valve_size_column_nam not in sheet.index:
            return results
        valves = sheet[valve_size_column_nam]
        tv = self.__get_time(sheet, time_name)
        for valve_number in valves.index:
            valve_data = valves[valve_number]
            results.append(TimeSeries(tv, valve_data))
        return results

    def get_well_construction_history(
        self,
        vfp_column_name: str = "VFP",
        valve_size_column_name: str = "Размер клапана",
    ) -> ConstructionHistory:
        vfp_data = self.__get_vfp_history(vfp_column_name)
        valve_data = self.__get_valve(valve_size_column_name)
        return ConstructionHistory(vfp_data, valve_data)


class RawExcelFile:
    def __init__(
        self,
        data: Union[Dict[str, RawExcelSheet], RawExcelSheet],
        path: Union[str, Path],
    ) -> None:

        if type(data) == dict:
            self.Data: Dict[str, RawExcelSheet] = data
        elif type(data) == RawExcelSheet:
            self.Data = dict()
            self.append(data)
        else:
            TypeError("'data' must to be str or Path")

        if type(path) == str:
            self.Path = Path(path)
        elif isinstance(path, Path):
            self.Path = path
        else:
            raise TypeError("'path' must to be str or Path")

    def __repr__(self) -> str:
        return f"ExcelFile: {self.Path}"

    def __getitem__(self, key: str) -> pd.DataFrame:
        return self.Data[key]

    def __contains__(self, item: str) -> bool:
        return item in self.Data.keys()

    def __iter__(self) -> Iterator[Tuple[str, RawExcelSheet]]:
        for key, value in self.Data.items():
            yield key, value

    def append(self, data: RawExcelSheet) -> None:
        self.Data[data.Name] = data

    def extend(self, data: List[RawExcelSheet]) -> None:
        for sheet in data:
            self.append(sheet)

    def get_folder(self) -> str:
        return str(self.Path.parent)

    def get_name(self) -> str:
        filename, file_extension = os.path.splitext(self.Path.name)
        return filename.strip()

    def get_extension(self) -> str:
        filename, file_extension = os.path.splitext(self.Path)
        return file_extension.strip()

    def get_well_measurement(
        self,
        sheet_name: str,
        regular_expression: str = r"Hist_(.*)",
    ) -> WellMeasurement:
        sheet = self.Data[sheet_name]
        return sheet.get_well_measurement()

    def get_construction_history(self, sheet_name: str) -> ConstructionHistory:
        sheet: RawExcelSheet = self.Data[sheet_name]
        return sheet.get_well_construction_history()

    def get_well_history(
        self,
        sheet_name: str,
        read_construction_history: bool = False,
        regular_expression: str = r"Hist_(.*)",
    ) -> WellHistory:
        wm = self.get_well_measurement(sheet_name)
        ch = self.get_construction_history(sheet_name)
        wname = re.findall(regular_expression, self.get_name())[0]
        additional_events = self.get_schedule_dataframe()
        return WellHistory(wname, wm, ch, additional_events=additional_events)

    def get_schedule_dataframe(self) -> Optional[ScheduleDataframe]:
        sdf = ScheduleDataframe()

        for key, value in self:
            if key in ScheduleKeyword.keys():
                sheet = value.get_events(keyword_name=key)
                if not sheet.empty():
                    sdf = sdf + sheet

        if sdf.empty():
            return None

        return sdf


class RawExcelDataDict:
    def __init__(
        self,
        data: Union[List[RawExcelFile], RawExcelFile] = None,
    ) -> None:
        self.Data: Dict[str, RawExcelFile] = dict()
        if data is None:
            pass
        elif type(data) == list:
            self.extend(data)
        elif type(data) == RawExcelFile:
            self.append(data)
        else:
            raise TypeError("Must to be Union[List[RowExcelData], RowExcelData")

    def __iter__(self) -> Iterator[RawExcelFile]:
        for value in self.Data.values():
            yield value

    def __getitem__(self, item: str) -> RawExcelFile:
        return self.Data[item]

    def items(self):
        return self.Data.items()

    def append(self, data: RawExcelFile) -> None:
        self.Data[data.get_name()] = data

    def extend(self, data: List[RawExcelFile]) -> None:
        for file in data:
            self.append(file)

    def get_schedule_date_frame(self) -> ScheduleDataframe:
        sdf = ScheduleDataframe()
        for file in self:
            w_sdf = file.get_schedule_dataframe()
            sdf = sdf + w_sdf
        return sdf

    def get_field_history(
        self,
        sheet_name: str = "Data",
        read_construction_history: bool = False,
        regular_expression: str = r"Hist_(.*)",
        other_event: bool = False,
    ) -> FieldHistory:
        fh = FieldHistory()
        for file in self:
            wh = file.get_well_history(
                sheet_name,
                read_construction_history,
                regular_expression,
            )
            fh.append(wh)

            if other_event:
                asdf = file.get_schedule_dataframe()
                if asdf is not None and fh.AddEvents is not None:
                    fh.AddEvents = fh.AddEvents + asdf
                elif fh.AddEvents is None:
                    fh.AddEvents = asdf

        return fh

    def get_strategy(self) -> Strategy:
        sdf = self.get_schedule_date_frame()
        return Strategy(sdf)
