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


class INIT(EclipseBinaryData):
    def __init__(
        self,
        data: Optional[EclipseBinaryData],
        inspec: Optional[EclipseBinaryData],
    ) -> None:
        self.Data = data
        self.INSPEC = inspec

    def __getattr__(self, item: str) -> Any:
        if hasattr(self.Data, item):
            return getattr(self.Data, item)
        elif hasattr(self.INSPEC, item):
            return getattr(self.INSPEC, item)
        else:
            raise super().__getattribute__(item)
