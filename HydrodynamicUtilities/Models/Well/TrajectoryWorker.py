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


class BaseMetaTrjData:
    pass


class Trajectory:
    def __init__(
        self,
        well_name: str,
        bore_number: int,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        meta_data: BaseMetaTrjData,
    ) -> None:
        self.WellName = well_name
        self.BoreNumber = bore_number
        # self.Revision = revision
        self.X = x
        self.Y = y
        self.Z = z
