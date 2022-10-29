from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..RawExcel import RawExcelFile
    from typing import Optional, List, Dict, Union

from ...Strategy import ScheduleDataframe, ScheduleSheet, Strategy
from ...Source.EclipseScheduleNames import FRACTURE_SPECS, WELSPECS, WELLTRACK

import pandas as pd
import numpy as np
import re

from copy import deepcopy


class FractureCreator:
    WellName = "Имя скважины"
    PatternName = "Имя Шаблона"

    @staticmethod
    def convert_sheet(df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=df.iloc[0]).drop(df.index[0])

    def convert_binding(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.convert_sheet(df)
        return df[~df[self.WellName].isna()]

    def convert_pattern(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.convert_sheet(df)
        return df[~df[self.PatternName].isna()].drop_duplicates()

    def get_welspecs(self, file: RawExcelFile) -> Optional[pd.DataFrame]:
        if "WELSPECS" in file:
            return self.convert_sheet(file["WELSPECS"].DF)
        else:
            return None

    def get_welltrack(self, file: RawExcelFile) -> Optional[pd.DataFrame]:
        if "WELLTRACK" in file:
            return self.convert_sheet(file["WELLTRACK"].DF)
        else:
            return None

    def get_start_time(
        self,
        row: pd.Series,
        welspec: Optional[pd.DataFrame],
        wname: str,
    ) -> np.datetime64:
        if welspec is None:
            return np.datetime64("nat")

        start = row["Дата ввода"]
        if pd.isna(start):
            welspec = welspec[welspec[WELSPECS.WellName].astype(str) == wname]
            if not welspec.empty:
                return np.datetime64(welspec["Time"].iloc[0])
            else:
                return np.datetime64("nat")

    @staticmethod
    def get_stop_time(row: pd.Series) -> np.datetime64:
        return row["Дата выбытия"]

    @staticmethod
    def get_bore(row: pd.Series) -> List[str]:
        data = str(row["Ствол"])
        data = re.subn(r"\s", "", data, flags=re.ASCII)[0]
        return data.split(",")

    @staticmethod
    def get_frack_name(wname: str, bore: str, frack_id: int) -> str:
        if frack_id < 10:
            return f"Frack_{wname}_{bore}0{str(frack_id)}"
        else:
            return f"Frack_{wname}_{bore}{str(frack_id)}"

    def get_md(
        self,
        welltrack: pd.DataFrame,
        row: pd.Series,
        bname: int,
    ) -> List[float]:
        wname = str(row[self.WellName]).upper()
        wtrack = welltrack[welltrack[WELLTRACK.WellName] == wname]
        btrack = wtrack[wtrack[WELLTRACK.BoreName] == bname]

        if btrack.empty:
            return [0] * row["Количество"]

        method = row["Точка привязки"]
        indent = row["Отступ"]
        delta = float(row["Длинна"])

        if method == "Конец":
            start_point = max(wtrack[WELLTRACK.MD].values) - indent
            end_point = start_point - delta
        elif method == "Конец":
            start_point = min(wtrack[WELLTRACK.MD].values) + indent
            end_point = start_point + delta
        else:
            raise KeyError

        numbe = row["Количество"]
        step = abs(end_point - start_point) / (numbe + 1)
        miv = min(start_point, end_point)
        mav = max(start_point, end_point)
        return list(np.arange(miv, mav, step))

    def get_fracture(self, file: RawExcelFile, wt_ss: ScheduleSheet) -> ScheduleSheet:
        try:
            binding = self.convert_binding(file["FrackBinding"].DF)
            pattern = self.convert_pattern(file["FrackPattern"].DF)
        except KeyError:
            return ScheduleSheet(FRACTURE_SPECS)

        welspec = self.get_welspecs(file)
        welltrack = wt_ss.DF

        results = pd.DataFrame()

        for rid, row in binding.iterrows():
            wname = row[self.WellName]
            pname = row["Имя патерна"]
            numbe = row["Количество"]
            start = self.get_start_time(row, welspec, str(wname))
            finis = self.get_stop_time(row)
            patte = pattern[pattern[self.PatternName] == pname]
            patte = patte.drop(self.PatternName, axis=1)
            for bore in self.get_bore(row):
                all_md = self.get_md(welltrack, row, int(bore))
                for frack_id in range(numbe):
                    frack_name = self.get_frack_name(wname, bore, frack_id)
                    p = deepcopy(patte)
                    p["Time"] = start
                    p[FRACTURE_SPECS.WellName] = wname
                    p[FRACTURE_SPECS.Bore] = bore
                    p[FRACTURE_SPECS.FracName] = frack_name
                    p[FRACTURE_SPECS.MD] = all_md.pop(0)
                    results = pd.concat([results, p])

        res = pd.DataFrame()
        for col in FRACTURE_SPECS.Order:
            res[col] = results[col]
        return results


class CompdatmdCreator:
    @staticmethod
    def convert_sheet(df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=df.iloc[0]).drop(df.index[0])

    @staticmethod
    def convert_binding(
        df: pd.DataFrame,
    ) -> Dict[Union[str, int], Dict[Union[str, int], str]]:
        df = df.dropna(how="all")
        well = df.iloc[2:, 0].values
        all_bore = df.iloc[1, 1:].values
        data = df.iloc[2:, 1:]
        results = dict()
        for wnid, wname in enumerate(well):
            results[wname] = dict()
            for bnid, bname in enumerate(all_bore):
                patern = data.iloc[wnid, bnid]
                if not pd.isna(patern):
                    results[wname][bnid] = patern
        return results

    def get_start_time(
        self,
        welspec: Optional[pd.DataFrame],
        wname: str,
    ) -> np.datetime64:
        if welspec is None:
            return np.datetime64("nat")

        welspec = welspec[welspec[WELSPECS.WellName].astype(str) == wname]
        if not welspec.empty:
            return np.datetime64(welspec["Time"].iloc[0])
        else:
            return np.datetime64("nat")

    def get_min_max_md(self):
        pass

    def get_compdatmd(
        self, file: RawExcelFile, ws_ss: ScheduleSheet, wt_ss: Optional[ScheduleSheet]
    ) -> ScheduleSheet:
        try:
            binding = self.convert_binding(file["FilterBinding"].DF)
            pattern = self.convert_sheet(file["FilterPattern"].DF)
        except KeyError:
            return ScheduleSheet(FRACTURE_SPECS)

        results = pd.DataFrame()

        for wname, bore_patterns in binding.items():
            start_time = self.get_start_time(ws_ss.DF, wname)
            for bore, bp in binding.items():
                start_md, end_md = 1, 1
                p = pattern[pattern["Имя Шаблона"] == bp]
                p["Time"] = start_time

        pass
