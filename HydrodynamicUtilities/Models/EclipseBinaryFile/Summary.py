from __future__ import annotations

import numpy as np
import pandas as pd

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Union, Dict, Any, Tuple, Optional, Iterable

from .BinaryData import EclipseBinaryData

from ..Time import TimeVector as Time
from typing import Iterable


class SUMMARYHeader:
    def __init__(
        self,
        keywords: np.ndarray,
        names: np.ndarray,
        num: np.ndarray,
        unit: np.ndarray,
    ) -> None:
        self.Keywords = keywords
        self.Names = names
        self.Num = num
        self.Unit = unit

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {len(self.Keywords)}"

    def __index(
        self,
        values: Union[List[str], str],
        param: str,
    ) -> Optional[np.ndarray]:
        if param == "keywords":
            vector = self.Keywords
        elif param == "names":
            vector = self.Names
        elif param == "num":
            vector = self.Num
        else:
            raise KeyError

        pattern: Optional[np.ndarray] = None

        if isinstance(values, (np.str, np.number, int, float)):
            pattern = vector == values

        else:
            for step in values:
                step_pattern = vector == step
                if pattern is None:
                    pattern = step_pattern
                else:
                    pattern = pattern | step_pattern

        return pattern

    def index(
        self,
        keywords: Union[List[str], str] = None,
        names: Union[List[str], str] = None,
        num: Union[List[str], str] = None,
    ) -> np.ndarray:
        if keywords is not None:
            keywords_pattern = self.__index(keywords, "keywords")
        else:
            keywords_pattern = np.ones(self.Keywords.shape) == 1

        if names is not None:
            names_pattern = self.__index(names, "names")
        else:
            names_pattern = np.ones(self.Names.shape) == 1

        if num is not None:
            num_pattern = self.__index(num, "num")
        else:
            num_pattern = np.ones(self.Num.shape) == 1

        if num_pattern is None:
            return np.ndarray([])
        elif names_pattern is None:
            return np.ndarray([])
        elif keywords_pattern is None:
            return np.ndarray([])
        else:
            pattern = keywords_pattern & names_pattern & num_pattern
            index: np.ndarray = np.arange(len(pattern))[pattern]
            return index

    def new(self, index: np.ndarray) -> SUMMARYHeader:
        new_keywords = self.Keywords[index]
        new_names = self.Names[index]
        new_num = self.Num[index]
        new_units = np.array(self.Unit)[index]
        return SUMMARYHeader(new_keywords, new_names, new_num, new_units)

    def names(self) -> List[str]:
        return list(self.Names)

    def well_name(self) -> List[str]:
        if "WOPR" in self.Keywords:
            index = self.index("WOPR", None, None)
            return list(self.Names[index])
        else:
            uniq_keywords = pd.unique(self.Keywords)
            for keywords in uniq_keywords:
                if keywords[0] == "W":
                    index = self.index(keywords, None, None)
                    return list(self.Names[index])
            return []

    def group_name(self) -> List[str]:
        if "GOPR" in self.Keywords:
            index = self.index("GOPR", None, None)
            return list(self.Names[index])
        else:
            uniq_keywords = pd.unique(self.Keywords)
            for keywords in uniq_keywords:
                if keywords[0] == "G":
                    index = self.index(keywords, None, None)
                    return list(self.Names[index])
            return []

    def keyword(self) -> List[str]:
        return list(pd.unique(self.Keywords))

    def nums(self) -> List[int]:
        return list(self.Unit)


class SUMMARY(EclipseBinaryData):
    def __init__(
        self,
        calc_name: str,
        values: np.ndarray,
        time_vector: Time,
        summary_header: SUMMARYHeader,
    ) -> None:
        self.CalcName = calc_name
        self.values = values
        self.TimeVector = time_vector
        self.Header = summary_header

    def __iter__(self) -> Iterable[SUMMARY]:
        for name in self.Header.Names:
            for key in self.Header.Keywords:
                for num in self.Header.Num:
                    yield self.get(key, name, num)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.values.shape}"

    def get(
        self,
        keywords: Union[List[str], str] = None,
        names: Union[List[str], str] = None,
        num: Union[List[str], str] = None,
    ) -> SUMMARY:
        index = self.Header.index(keywords, names, num)
        new_df = self.values[:, index]
        new_header = self.Header.new(index)
        return SUMMARY(self.CalcName, new_df, self.TimeVector, new_header)

    @property
    def shape(self) -> Tuple[int, int]:
        i, j = self.values.shape[0], self.values.shape[1]
        return i, j

    def get_well_names(self) -> List[str]:
        return self.Header.well_name()

    def get_group_name(self) -> List[str]:
        return self.Header.group_name()


class SUMMARYList(list):
    pass
