from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import pandas as pd
from pathlib import Path
from typing import Tuple
from HydrodynamicUtilities.Models.Well import WellTrajectoryDataFrame
import re
import os


class ReaderSchlumbergerExcel:
    brs = r"Well_(.*)[\s*]Rev_(.*)[\s*]BH(.*)[\s*]Slot(.*)(\s)(.*)"
    target_sheet = "Every 10m"
    number_header = 22
    x_col_name = "Northing\n(m)"
    y_col_name = "Easting\n(m)"
    z_col_name = "TVDSS\n(m)"

    logging = True

    def log(self, file_name: str, *args: Any, **kwargs: Any) -> None:
        print(f"Read: {file_name}")

    @staticmethod
    def name_from_regular_string(
        xls_name: str, regular_string: str = brs
    ) -> Tuple[str, int, str]:
        data = re.findall(regular_string, xls_name)[0]
        well_name = data[0]
        bore_name = int(data[2])
        rev_name = f"Rev_{data[1]}"
        return well_name, bore_name, rev_name

    def read_file(
        self,
        link: Path,
        wdf: WellTrajectoryDataFrame = None,
    ) -> WellTrajectoryDataFrame:
        if wdf is None:
            wdf = WellTrajectoryDataFrame()

        wname, bname, rname = self.name_from_regular_string(str(link))

        df = pd.read_excel(
            link, sheet_name=self.target_sheet, header=self.number_header
        )
        v_id = 0
        for v_id, value in enumerate(df["MD\n(m)"].values):
            if pd.isna(value):
                break
        df = df.iloc[:v_id]

        wdf.append(
            wname,
            bname,
            rname,
            x=df[self.y_col_name].astype(float).values,
            y=df[self.x_col_name].astype(float).values,
            z=df[self.z_col_name].astype(float).values,
        )
        if self.logging:
            self.log(str(link))
        return wdf

    def read_folder(self, link: Path) -> WellTrajectoryDataFrame:
        wdf = WellTrajectoryDataFrame()
        for file in os.listdir(link):
            file_link = link / file
            if file_link.is_file():
                try:
                    wdf = self.read_file(file_link, wdf)
                except PermissionError:
                    self.log(f"Permission denied: {file_link}")

        return wdf
