from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Union, Dict, Any, Tuple, Optional, Iterable

from .BinaryData import EclipseBinaryData

import numpy as np
import pandas as pd

from ..Time import TimeVector as Time
from ..ParamVector import TimeSeries
from ..ParamVector import RateTimeSeriasParam, CumTimeSeriasParam
from copy import deepcopy


class UNRSTRSSPEC(EclipseBinaryData):
    def __init__(
        self,
        unrst: Optional[EclipseBinaryData],
        rsspec: Optional[EclipseBinaryData],
    ) -> None:
        self.UNRST = unrst
        self.RSSPEC = rsspec

    def __getattr__(self, item: str) -> Any:
        if hasattr(self.UNRST, item):
            return getattr(self.UNRST, item)
        elif hasattr(self.RSSPEC, item):
            return getattr(self.RSSPEC, item)
        else:
            raise super().__getattribute__(item)
