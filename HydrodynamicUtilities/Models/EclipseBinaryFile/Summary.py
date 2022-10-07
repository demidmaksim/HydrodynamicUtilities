from __future__ import annotations

import numpy as np
import pandas as pd

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Union, Dict, Any, Tuple, Optional, Iterable

from .BinaryData import EclipseBinaryData

from ..Time import TimeVector as Time
from typing import Iterable
from ..ParamVector import TimeSeries
from copy import deepcopy

import pandas as pd


class SUMMARYHeader:
    def __init__(
        self,
        keywords: np.ndarray,
        names: np.ndarray,
        num: np.ndarray,
        unit: np.ndarray,
    ) -> None:
        self.Keywords = keywords.astype(str)
        self.Names = names.astype(str)
        self.Num = num.astype(int)
        self.Unit = unit.astype(str)

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

    def replace_name(
        self,
        obj_name: Dict[Union[str, int], Iterable[Union[str, int]]] = None,
        # num_name: Dict[Union[str, int], Iterable[Union[str, int]]] = None,
    ) -> SUMMARYHeader:

        new = deepcopy(self)

        if obj_name is not None:
            for new_name, old_names in obj_name.items():
                for on in old_names:
                    new.Names[new.Names == on] = new_name

        """
        if num_name is not None:
            for new_name, old_names in num_name.items():
                for on in old_names:
                    new.Num[new.Num == on] = new_name
        """

        return new

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame()
        df["Keyword"] = self.Keywords.astype(str)
        df["Name"] = self.Names.astype(str)
        df["Num"] = self.Num.astype(int)
        df["Unit"] = self.Unit.astype(str)
        return df

    def duplicated(self) -> pd.DataFrame:
        df = self.to_dataframe()
        duplicate = df.duplicated(keep=False)
        df["Duplicate"] = duplicate
        return df

    def compact(self) -> SUMMARYHeader:
        df = self.to_dataframe()
        duplicate = df.duplicated()
        uniq = df[duplicate]
        return SUMMARYHeader(
            uniq["Keyword"].values,
            uniq["Name"].values,
            uniq["Num"].values,
            uniq["Unit"].values,
        )


class SUMMARY(EclipseBinaryData):

    __well_flow_keyword = (
        "WOPR",
        "WWPR",
        "WGPR",
        "WOIR",
        "WWIR",
        "WGIR",
    )

    __well_total_keyword = (
        "WOPT",
        "WWPT",
        "WGPT",
        "WOIT",
        "WWIT",
        "WGIT",
    )

    __well_pressure = (
        "WBHP",
        "WTHP",
    )

    __wel_reservoir_rate_conditions = (
        "WOVPR",
        "WWVPR",
        "WGVPR",
        "WOVIR",
        "WWVIR",
        "WGVIR",
    )

    __wel_reservoir_total_conditions = (
        "WOVPT",
        "WWVPT",
        "WGVPT",
        "WOVIT",
        "WWVIT",
        "WGVIT",
    )

    __segment_flow = (
        "SOFR",
        "SWFR",
        "SGFR",
    )

    __segment_total = (
        "SOFT",
        "SWFT",
        "SGFT",
    )

    __segment_pressure = (
        "SPR",
        "SPRD",
    )

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
        keywords: Union[Iterable[str], str] = None,
        names: Union[Iterable[str], str] = None,
        num: Union[Iterable[str], str] = None,
    ) -> SUMMARY:
        index = self.Header.index(keywords, names, num)
        new_df = self.values[:, index]
        new_header = self.Header.new(index)
        return SUMMARY(self.CalcName, new_df, self.TimeVector, new_header)

    def get_request(
        self,
        well_flow: bool = False,
        well_total: bool = False,
        well_pressure: bool = False,
        wel_reservoir_rate_conditions: bool = False,
        wel_reservoir_total_conditions: bool = False,
        segment_flow: bool = False,
        segment_total: bool = False,
        segment_pressure: bool = False,
    ) -> SUMMARY:
        target_kw = []
        if well_flow:
            target_kw.extend(self.__well_flow_keyword)
        if well_total:
            target_kw.extend(self.__well_total_keyword)
        if well_pressure:
            target_kw.extend(self.__well_pressure)
        if wel_reservoir_rate_conditions:
            target_kw.extend(self.__wel_reservoir_rate_conditions)
        if wel_reservoir_total_conditions:
            target_kw.extend(self.__wel_reservoir_total_conditions)
        if segment_flow:
            target_kw.extend(self.__segment_flow)
        if segment_total:
            target_kw.extend(self.__segment_total)
        if segment_pressure:
            target_kw.extend(self.__segment_total)

        return self.get(keywords=target_kw)

    def to_time_series(self) -> TimeSeries:
        if self.shape[1] != 1:
            raise ValueError
        return TimeSeries(self.TimeVector, self.values.T[0])

    @property
    def shape(self) -> Tuple[int, int]:
        i, j = self.values.shape[0], self.values.shape[1]
        return i, j

    def get_well_names(self) -> List[str]:
        return self.Header.well_name()

    def get_group_name(self) -> List[str]:
        return self.Header.group_name()

    def replace_name_from_df(
        self,
        df: pd.DataFrame,
        old_wname: str = "Скважина в модели",
        new_wname: str = "Скважина",
        old_sname: str = "Сегмент",
        new_sname: str = "Пачка",
    ) -> SUMMARY:
        well_target_df = df[[old_wname, new_wname]]
        well_results = dict()
        for well in pd.unique(well_target_df[new_wname]):
            val = well_target_df[well_target_df[new_wname] == well].values
            well_results[well] = pd.unique(val.T[0])

        segm_target_df = df[[old_sname, new_sname]]
        segm_results = dict()
        for segm in pd.unique(segm_target_df[new_sname]):
            val = segm_target_df[segm_target_df[new_sname] == segm].values
            segm_results[segm] = pd.unique(val.T[0])

        return self.replace_name(obj_name=well_results, num_name=segm_results)

    def replace_name(
        self,
        obj_name: Dict[Union[str, int], Iterable[Union[str, int]]] = None,
        # num_name: Dict[Union[str, int], Iterable[Union[str, int]]] = None,
    ) -> SUMMARY:
        new_header = self.Header.replace_name(obj_name)
        return SUMMARY(self.CalcName, self.values, self.TimeVector, new_header)

    def compact(self) -> SUMMARY:
        new = deepcopy(self)
        df = self.Header.duplicated()
        duplicate_df = df[df["Duplicate"]]
        uniq_duplicate = duplicate_df[["Keyword", "Name", "Num"]].drop_duplicates()
        for_del = []
        for rid, row in uniq_duplicate.iterrows():
            target_df = duplicate_df[
                (duplicate_df["Keyword"] == row["Keyword"])
                & (duplicate_df["Name"] == row["Name"])
                & (duplicate_df["Num"] == row["Num"])
            ]
            target_value = self.values[:, target_df.index.values]
            new_value = np.sum(target_value, axis=1)
            new.values[:, rid] = new_value
            target_for_del = target_df[target_df.index.values != rid]
            for_del.extend(target_for_del.index.values)
            pass
        pattern = np.ones(self.values.shape[1]).astype(bool)
        pattern[for_del] = False
        new.values = new.values[:, pattern]
        new.Header = self.Header.compact()
        return new


class FieldSUMMARY:
    def __init__(
        self, wells: Iterable[WellSUMMARY], group: Iterable[WellSUMMARY]
    ) -> None:
        self.Wells = wells
        self.Group = group


class GroupSUMMARY:
    def __init__(self, data: SUMMARY) -> None:
        self.Data = data


class WellSUMMARY:
    def __init__(
        self,
        well_head_summary: WellHeadSUMMARY,
        segment_summary: Iterable[SegmentSUMMARY],
    ) -> None:
        self.WellHead = well_head_summary
        self.Segments = list(segment_summary)


class WellHeadSUMMARY:
    def __init__(self, data: SUMMARY) -> None:
        self.Data = data


class SegmentSUMMARY:
    def __init__(self, data: SUMMARY) -> None:
        self.Data = data


class SUMMARYList(list):
    pass
