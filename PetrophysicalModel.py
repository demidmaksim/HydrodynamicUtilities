from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable

import re
import numpy as np


class Model:
    __re = "\+|\*|-|\/|\(|\)|\="

    def __init__(self, poro, clay, cub_arithmetic: Iterable[str]) -> None:
        self.PORO = poro
        self.CLAY = clay
        for val in cub_arithmetic:
            self.calc(val)

    def calc(self, value: str) -> None:
        value = value.upper().strip()
        new_value = value[value.index("=") + 1 :]
        new_value = re.split(self.__re, new_value)
        for point in new_value:
            point = point.strip()
            if point not in ("", "EXP", "LN"):
                try:
                    point = float(point)
                except ValueError:
                    exec(f"{point}=self.{point}")

        value = re.subn(r"EXP", "np.exp", value, flags=re.ASCII)[0]
        value = re.subn(r"LN", "np.log", value, flags=re.ASCII)[0]
        exec(f"self.{value}")
