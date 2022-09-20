import xlsxwriter as xlsw
from HydrodynamicModelAnalysis.Models.EclipseBinaryFile import SUMMARY
from HydrodynamicModelAnalysis.Models import TimePoint, generate_time_vector
from HydrodynamicModelAnalysis.Models import create_from_summary, PeriodCalcResults

import pandas as pd


def data_preparation(
    summary: SUMMARY, start: TimePoint, end: TimePoint, step: str, value_step: int
) -> PeriodCalcResults:
    target_param = (
        "WOPT",
        "WWPT",
        "WGPT",
        "WWIT",
        "WGIT",
        # "WBHP",
        # "WBP9",
        "WWTT",
    )

    tv = generate_time_vector(start, end, step, value_step)
    df = create_from_summary(summary, target_param)
    models = df.to_inter_model()
    return models.to_period_results(tv)


def create(
    summary: SUMMARY,
    start: TimePoint,
    end: TimePoint,
    step: str,
    value_step: int,
    file_name: str = "Test.xlsx",
) -> None:
    data = data_preparation(summary, start, end, step, value_step)
    book = xlsw.Workbook(file_name)
    sheet = book.add_worksheet("Data")
    sheet.merge_range(0, 0, 1, 0, "Месторождение")
    sheet.merge_range(0, 1, 1, 1, "Объект")
    sheet.merge_range(0, 2, 1, 2, "Скважина")
    sheet.merge_range(0, 3, 1, 3, "Период")
    sheet.merge_range(0, 4, 1, 4, "Начало")
    sheet.merge_range(0, 5, 1, 5, "Окончание")
    sheet.merge_range(0, 6, 1, 6, "Время работы")
    sheet.merge_range(0, 7, 0, 9, "Время работы")
    sheet.merge_range(0, 10, 0, 12, "Закачка")
    sheet.merge_range(0, 13, 0, 14, "Давление")

    sheet.write(1, 7, "Нефть")
    sheet.write(1, 8, "Вода")
    sheet.write(1, 9, "Газ")

    sheet.write(1, 10, "Нефть")
    sheet.write(1, 11, "Вода")
    sheet.write(1, 12, "Газ")

    sheet.write(1, 13, "BHP")
    sheet.write(1, 14, "THP")

    sheet.write_row(
        3,
        0,
        (
            "---",
            "---",
            "---",
            "---",
            "---",
            "---",
            "сут",
            "ст. м3",
            "ст. м3",
            "ст. м3",
            "ст. м3",
            "ст. м3",
            "ст. м3",
            "Бар",
            "Бар",
        ),
    )

    sheet.write_row(4, 0, range(1, 16))

    i = 0
    for obj in pd.unique(data.df[data.ObjectName].values):
        obj_data = data.get_object(obj)

        if obj_data is None:
            raise ValueError

        for pid, param in enumerate(pd.unique(data.df[data.ParamName].values)):

            pdata = obj_data.get_param(param)

            if pdata is None:
                raise ValueError

            if pid == 0:
                sheet.write_column(5 + i, 2, pdata.df[data.ObjectName].values)
                sheet.write_column(5 + i, 3, pdata.df[data.PeriodName].values)
                sheet.write_column(5 + i, 4, pdata.df[data.StartPeriod].values)
                sheet.write_column(5 + i, 5, pdata.df[data.EndPeriod].values)

            if param == "WWTT":
                sheet.write_column(5 + i, 6, pdata.df[data.Value].values)
            if param == "WOPT":
                sheet.write_column(5 + i, 7, pdata.df[data.Value].values)
            if param == "WWPT":
                sheet.write_column(5 + i, 8, pdata.df[data.Value].values)
            if param == "WGPT":
                sheet.write_column(5 + i, 9, pdata.df[data.Value].values)
            if param == "WOIT":
                sheet.write_column(5 + i, 10, pdata.df[data.Value].values)
            if param == "WWIT":
                sheet.write_column(5 + i, 11, pdata.df[data.Value].values)
            if param == "WGIT":
                sheet.write_column(5 + i, 12, pdata.df[data.Value].values)

            if pid == len(pd.unique(data.df[data.ParamName].values)) - 1:
                i += len(pdata.df.values)

    book.close()
