from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Union

import numpy as np
import pandas as pd

from HydrodynamicUtilities.Models.HistoryData import WellMeasurement
from HydrodynamicUtilities.Models.Time import TimeVector


class ConvertorToRateWellData:
    Days = ("Время", "Дата")
    Hour = ("Время", "Час")

    THP = ("Давление", "Рбуфер")
    BHP = ("Глубинные датчики", "Р в НКТ")

    OilProduction = ("Дебит", "Нефть")
    WatProduction = ("Дебит", "Вода")
    GasProduction = ("Дебит", "Газ")

    OilInjection = ("Приемистость", "Нефть")
    WatInjection = ("Приемистость", "Вода")
    GasInjection = ("Приемистость", "Газ")

    OilDensity = ("Плотность", "Нефть")
    WatDensity = ("Плотность", "Вода")
    GasDensity = ("Плотность", "Газ")

    Status = ("Состояние скважины", "Режим работы")
    WellType = ("Состояние скважины", "Tип")

    Order = (
        THP,
        BHP,
        OilProduction,
        WatProduction,
        GasProduction,
        OilInjection,
        WatInjection,
        GasInjection,
        Status,
    )

    Mode = "Режим работы"
    InWork = "В работе"
    OutWork = "Остановлена"
    target_sheet = "Data"

    @staticmethod
    def read_column(
        table: pd.DataFrame,
        column_names: Tuple[str, ...],
    ) -> Union[pd.DataFrame, pd.Series]:
        column = table
        for name in column_names:
            column = column[name]
        return column

    def convert(self, table: pd.DataFrame, time: TimeVector) -> WellMeasurement:

        whd = WellMeasurement(time=time)

        for hid, header in enumerate(self.Order):
            column = self.read_column(table, header)
            if WellMeasurement.WhiteList[hid] == "Status":
                new_column = np.zeros(column.shape)
                new_column[column == self.InWork] = 1
                column = new_column

            setattr(whd, WellMeasurement.WhiteList[hid], column)
        return whd
