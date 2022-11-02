from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Dict, Optional, Union, Any, Tuple

import re
import numpy as np

from typing import Iterable, Dict


class Slider:
    pass


class Model:
    __re = "\+|\*|-|\/|\(|\)|\="
    __base_param = ("IndepVar", "BaseValues", "Arithmetic", "DepVar", "__Slider")

    def __init__(
            self,
            independent_variables: Union[Dict[str, Optional[np.ndarray]], Iterable[str]],
            cub_arithmetic: Iterable[str]
    ) -> None:

        if isinstance(independent_variables, Dict):
            self.IndepVar = tuple(independent_variables.keys())
            self.BaseValues = dict()
            for key, val in independent_variables.items():
                if val is not None:
                    self.BaseValues[key] = val
        elif isinstance(independent_variables, Iterable):
            self.IndepVar = tuple(independent_variables)
            self.BaseValues: Optional[Dict[str, np.ndarray]] = None
        else:
            raise TypeError

        self.Arithmetic = cub_arithmetic
        self.DepVar = self.__init_arithmetic(cub_arithmetic)

        self.__Slider = Slider()

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self.__base_param:
            super().__setattr__(key, value)
        elif key in self.DepVar:
            raise TypeError
        else:
            super().__setattr__(key, value)

    def __getattr__(self, key: str) -> Optional[np.ndarray]:
        if key in self.__base_param:
            if key in self.BaseValues.keys():
                return self.BaseValues[key]
            else:
                return None
        elif key in self.DepVar:
            if key in self.DepVar:
                return self.__Slider.__getattribute__(key)
        else:
            return super().__getattribute__(key)

    @staticmethod
    def __init_arithmetic(cub_arithmetic: Iterable[str]) -> Tuple[str, ...]:
        results = list()
        for string in cub_arithmetic:
            param = string.split("=")[0].strip()
            results.append(param)
        return tuple(set(results))

    def all_calc(self, independent_variables: Dict[str, np.ndarray] = None) -> None:
        if independent_variables is None:
            ind_var = dict()
            for param in self.IndepVar:
                if param not in self.BaseValues:
                    ind_var[param] = np.arange(0, 1.1, 0.1)
                else:
                    ind_var[param] = self.BaseValues[param]
        else:
            ind_var = independent_variables

        for expression in self.Arithmetic:
            self.calc(expression, **ind_var)

    def calc(self, value: str, **kwargs: Dict[str, np.ndarray]) -> None:

        for key in kwargs:
            exec(f"{key.upper()}=kwargs['{key}']")

        value = value.upper().strip()
        new_value = value[value.index("=") + 1 :]
        new_value = re.split(self.__re, new_value)
        for point in new_value:
            point = point.strip()
            if point not in ("", "EXP", "LN") and point not in self.BaseValues:
                try:
                    point = float(point)
                except ValueError:
                    exec(f"{point}=self._Model__Slider.{point}")

        value = re.subn(r"EXP", "np.exp", value, flags=re.ASCII)[0]
        value = re.subn(r"LN", "np.log", value, flags=re.ASCII)[0]
        exec(f"self._Model__Slider.{value}")
