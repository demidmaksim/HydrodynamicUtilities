from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import Type, Any

from ..ExcelFile import RawExcelSheet, RawExcelFile, RawExcelDataDict
from ..ExcelFile.RawExcel import convert_to_schedule_sheet_format
from ..Source.EclipseScheduleNames import (
    ScheduleKeyword,
    BaseKeyWord,
    WELLTRACK,
)


class Validator:
    @staticmethod
    def log(text: str, log_type: str) -> None:
        if log_type == "Error":
            print(f"  {text}")
        else:
            print(text)

    @classmethod
    def __check_row_must_to_be(
        cls,
        template: Type[BaseKeyWord],
        row: pd.Series,
        row_id: int,
    ) -> None:
        for column in template.MustToBe:
            value = row[column]
            if pd.isna(value):
                cls.log(
                    f"In the line {row_id + 1} the parameter "
                    f"'{column}' must have the value",
                    "Error",
                )

    @classmethod
    def __check_row_additional_control(
        cls,
        template: Type[BaseKeyWord],
        row: pd.Series,
        row_id: int,
    ) -> None:
        if template.AdditionalControl is not None:
            column = template.AdditionalControl
            val = row[column]
            if val not in template.AdditionalMustToBe.keys():
                cls.log(
                    f"In the line {row_id + 1} the parameter "
                    f"'{column}' must have the value",
                    "Error",
                )

            if pd.isna(val):
                return None

            type_control = template.AdditionalMustToBe[val]
            if type_control is None:
                pass
            elif isinstance(type_control, str):
                value = row[type_control]
                if pd.isna(value):
                    cls.log(
                        f"In the line {row_id + 1} the parameter "
                        f"'{type_control}' must have the value ",
                        "Error",
                    )
            elif isinstance(type_control, list):
                for col in type_control:
                    value = row[col]
                    if pd.isna(value):
                        cls.log(
                            f"In the line {row_id + 1} the parameter "
                            f"'{type_control}' must have the value ",
                            "Error",
                        )

    @classmethod
    def __check_row_type_var(cls, value: Any) -> bool:
        try:
            value = str(value)
        except ValueError:
            return False

        if "@" == value[0] and "@" == value[-1] and len(value) > 2:
            return True
        else:
            return False

    @classmethod
    def __check_row_type(
        cls,
        template: Type[BaseKeyWord],
        row: pd.Series,
        row_id: int,
    ) -> None:
        for vid, value in enumerate(row.values):
            col_type = template.ColumnType[vid]

            if col_type == str:
                pass
            elif isinstance(value, col_type):
                pass
            elif pd.isna(value):
                pass
            elif isinstance(value, int) and col_type == float:
                pass
            elif isinstance(value, str):
                try:
                    col_type(value)
                except ValueError:
                    if not cls.__check_row_type_var(value):
                        col = row.index[vid]
                        t = f"Сheck data in row {row_id + 1} and column {col}'"
                        cls.log(t, "Error")
            else:
                col = row.index[vid]
                t = f"Сheck data in row {row_id + 1} and column {col}'"
                cls.log(t, "Error")

    @classmethod
    def __check_time(
        cls,
        template: Type[BaseKeyWord],
        row: pd.Series,
        row_id: int,
    ) -> None:
        time = row.iloc[0]
        if pd.isna(time):
            cls.log(f"  String {row_id + 1} is missing a date", "Warning")

    @classmethod
    def check_row(cls, sheet: RawExcelSheet) -> None:
        template = ScheduleKeyword()[sheet.Name]
        df = convert_to_schedule_sheet_format(sheet.DF)

        for row_id, row in df.iterrows():
            rid = int(str(row_id))
            row1 = row.iloc[1:]
            cls.__check_time(template, row, rid)
            cls.__check_row_must_to_be(template, row1, rid)
            cls.__check_row_additional_control(template, row1, rid)
            cls.__check_row_type(template, row1, rid)

    @classmethod
    def check_welltrack(cls, sheet: RawExcelSheet) -> None:
        pass

    @classmethod
    def check_column_name(cls, sheet: RawExcelSheet) -> None:
        template = ScheduleKeyword()[sheet.Name]
        df = convert_to_schedule_sheet_format(sheet.DF)
        error = False
        for column in template.Order:
            if column not in df.columns:
                cls.log(f"collumn '{column}' not in sheet", "Error")
                error = True

        if not error:
            t = f"Required columns in sheet {sheet.Name} are present"
            cls.log(t, "Correct")

    @classmethod
    def check_sheet_name(cls, file: RawExcelFile) -> None:
        for s_name, sheet in file:
            if s_name not in ScheduleKeyword.keys():
                cls.log(f"sheet '{s_name}' skipped", "Correct")
            elif s_name == WELLTRACK.__name__:
                cls.check_column_name(sheet)
                cls.check_welltrack(sheet)
            else:
                cls.check_column_name(sheet)
                cls.check_row(sheet)

    @classmethod
    def check(cls, files: RawExcelDataDict) -> None:
        for file in files:
            cls.check_sheet_name(file)
