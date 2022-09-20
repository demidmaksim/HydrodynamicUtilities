from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Tuple, List, Dict, Iterator
    import numpy as np

    arraylike = Union[
        List[Union[int, float]],
        Tuple[Union[int, float]],
        np.ndarray,
    ]
    single_numbers = Union[float, int]
    numbers = Union[arraylike, single_numbers]

import pandas as pd
import numpy as np

from pathlib import Path
from matplotlib import pyplot as plt
from copy import deepcopy
from scipy.interpolate import interp1d

from ..Strategy.Frame import ScheduleDataframe, ScheduleSheet
from ..Source.EclipseScheduleNames import WELLTRACK


class Trajectory:
    def __init__(
        self,
        well_name: str,
        bore_number: int,
        revision: str,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        zero_point: np.ndarray = None,
        base_angle: Union[int, float] = None,
        angle_unit: str = "deg",
    ) -> None:
        self.WellName = well_name
        self.BoreNumber = bore_number
        self.Revision = revision
        self.X = x
        self.Y = y
        self.Z = z
        self.__XModel = interp1d(self.md, self.X, copy=False)
        self.__YModel = interp1d(self.md, self.Y, copy=False)
        self.__ZModel = interp1d(self.md, self.Z, copy=False)
        self.__MDModel = interp1d(self.Z, self.md, copy=False)

    def copy(self) -> Trajectory:
        return deepcopy(self)

    @property
    def md(self) -> np.ndarray:
        x_component = (self.X[:-1] - self.X[1:]) ** 2
        y_component = (self.Y[:-1] - self.Y[1:]) ** 2
        z_component = (self.Z[:-1] - self.Z[1:]) ** 2
        md = (x_component + y_component + z_component) ** 0.5
        results: np.ndarray = np.zeros(self.X.shape)
        results[1:] = md.cumsum()
        return results

    def z(self, md: Union[arraylike, numbers]) -> np.ndarray:
        results: np.ndarray = self.__ZModel(md)
        return results

    def tvd_to_md(self, tvd: Union[arraylike, numbers]) -> np.ndarray:
        results: np.ndarray = self.__MDModel(tvd)
        return results

    def x(self, md: Union[arraylike, numbers]) -> np.ndarray:
        results: np.ndarray = self.__XModel(md)
        return results

    def y(self, md: Union[arraylike, numbers]) -> np.ndarray:
        results: np.ndarray = self.__YModel(md)
        return results

    def to_schedule_dataframe(self) -> ScheduleDataframe:
        ss = ScheduleSheet(WELLTRACK)
        ss.X = self.X
        ss.Y = self.Y
        ss.Z = self.Z
        ss.MD = self.md
        ss.WellName = f"{self.WellName}_{self.Revision}"
        ss.BoreName = self.BoreNumber
        ss.PointNumber = np.arange(len(self.X))
        return ScheduleDataframe() + ss
