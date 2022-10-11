from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Iterable

import pandas as pd
import numpy as np

from .TrajectoryWorkerOld import Trajectory
from copy import deepcopy
from ..Strategy.Frame import ScheduleDataframe, ScheduleSheet
from ..Source.EclipseScheduleNames import WELLTRACK
from pathlib import Path


class WellTrajectoryDataFrame:

    Well = "Well"
    Rev = "Rev"
    Bore = "Bore"
    Index = "Index"
    X = "X"
    Y = "Y"
    Z = "Z"

    def __init__(self) -> None:
        self.df = pd.DataFrame()

    def __iter__(self) -> Iterable[Trajectory]:
        df = self.report(True)
        df = df.sort_values(by=[self.Well, self.Rev, self.Bore])
        for rid, row in df.iterrows():
            wname = row[self.Well]
            bname = row[self.Bore]
            rname = row[self.Rev]
            yield self.get_welltrack(wname, bname, rname, False)

    def get_well_names(self) -> List[str]:
        wname = pd.unique(self.df[self.Well].values)
        wname = wname.astype(str)
        return list(wname)

    def get_bores_name(self) -> List[int]:
        wname = pd.unique(self.df[self.Bore].values)
        wname = wname.astype(int)
        return list(wname)

    def append(
        self,
        well: str,
        bore: int,
        rev: str,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
    ):
        df = pd.DataFrame()
        df[self.X] = x
        df[self.Y] = y
        df[self.Z] = z
        df[self.Well] = well
        df[self.Rev] = rev
        df[self.Bore] = bore
        df[self.Index] = df.index.to_numpy()

        self.df = pd.concat((self.df, df), ignore_index=True)

    def choose(
        self,
        well_name: str = None,
        bore: int = None,
        rev: str = None,
        confiscate: bool = True,
    ) -> WellTrajectoryDataFrame:
        if well_name is not None:
            wnp = self.df[self.Well].values == well_name
        else:
            wnp = np.ones(self.df[self.Well].value.shape)

        if bore is not None:
            wbp = self.df[self.Bore].values == bore
        else:
            wbp = np.ones(self.df[self.Bore].value.shape)

        if rev is not None:
            wrp = self.df[self.Rev].values == rev
        else:
            wrp = np.ones(self.df[self.Rev].value.shape)

        pattern = wnp * wbp * wrp

        if confiscate:
            self.df = self.df[~pattern]

        results = WellTrajectoryDataFrame()
        results.df = self.df[pattern]
        return results

    def report(self, bore: bool = False) -> pd.DataFrame:
        results = deepcopy(self.df)
        results = results.drop(self.X, axis=1)
        results = results.drop(self.Y, axis=1)
        results = results.drop(self.Z, axis=1)
        results = results.drop(self.Index, axis=1)
        if not bore:
            results = results.drop(self.Bore, axis=1)
        results = results.drop_duplicates()
        return results

    def get_welltrack(
        self,
        well_name: str,
        bore: int,
        rev: str,
        confiscate: bool = True,
    ) -> Optional[Trajectory]:
        new = self.choose(well_name, bore, rev, confiscate)
        if len(new.df) == 0:
            return None
        else:
            return Trajectory(
                well_name,
                bore,
                rev,
                new.df[self.X].values,
                new.df[self.Y].values,
                new.df[self.Z].values,
            )

    def to_well_list(self) -> None:
        pass

    def to_schedule_dataframe(self) -> ScheduleDataframe:
        sdf = ScheduleDataframe()
        for trj in self:
            sdf = sdf + trj.to_schedule_dataframe()
        return sdf

    def get_well_name(self) -> List[str]:
        return list(pd.unique(self.df[self.Well]).astype(str))

    def to_petrel(self, path: Path) -> None:
        results = []
        for well in self.get_well_name():
            well_df = self.df[self.df[self.Well] == well]
            for rev in pd.unique(well_df[self.Rev]):
                rev_df = well_df[well_df[self.Rev] == rev]
                for bore in pd.unique(rev_df[self.Bore]):
                    bore_df = rev_df[rev_df[self.Bore] == bore]
                    bore_df = bore_df.sort_values(by=self.Index)
                    mdf = pd.DataFrame()
                    mdf["X"] = bore_df["X"]
                    mdf["Y"] = bore_df["Y"]
                    mdf["Z"] = -bore_df["Z"]
                    data = mdf.to_string(
                        col_space=12,
                        # justify="inherit",
                        index=False,
                        header=False,
                        na_rep="1*",
                        float_format="%.2f",
                    )
                    str_data = f"#WELL NAME:\t{well}_{rev}%{well}_{rev}_{bore}\n{data}"
                    results.append(str_data)
        str_results = "\n".join(results)
        with open(path, "w") as file:
            file.write(str_results)
