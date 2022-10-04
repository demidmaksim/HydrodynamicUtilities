from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Union


import pandas as pd
import numpy as np

from .TrajectoryWorkerOld import Trajectory


class WellList:
    def __init__(self, data: List[Trajectory] = None) -> None:
        if data is not None:
            self.Data = data
        else:
            self.Data = data
