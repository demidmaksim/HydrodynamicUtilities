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
from ..ParamVector import RateTimeSeriasParam, CumTimeSeriasParam
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
        try:
            self.Num = num.astype(int)
        except ValueError:
            self.Num = num.astype(object)
        self.Unit = unit.astype(str)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {len(self.Keywords)}"

    def __index(
        self,
        values: Union[List[str], str],
        param: str,
    ) -> Optional[np.ndarray]:
        if param == "keywords":
            vector = self.Keywords.astype(str)
        elif param == "names":
            vector = self.Names.astype(str)
        elif param == "num":
            vector = self.Num.astype(str)
        else:
            raise KeyError

        pattern: Optional[np.ndarray] = None

        if isinstance(values, (np.str, np.number, int, float)):
            pattern = vector == str(values)

        else:
            for step in values:
                step_pattern = vector == str(step)
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
        index = self.get_group_index("wel")
        wname = pd.unique(self.Names[index])
        return list(wname)

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
        try:
            df["Num"] = self.Num.astype(int)
        except ValueError:
            df["Num"] = self.Num.astype(object)
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

    def get_group_index(self, key: str) -> np.ndarray:
        df = self.to_dataframe()
        if key.lower() == "seg":
            return df["Keyword"].str.contains(r"\bS.*", regex=True).values
        if key.lower() == "wel":
            return df["Keyword"].str.contains(r"\bW.*", regex=True).values
        else:
            raise KeyError


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
        self.Values = values
        self.TimeVector = time_vector
        self.Header = summary_header

    def __iter__(self) -> Iterable[SUMMARY]:
        for name in self.Header.Names:
            for key in self.Header.Keywords:
                for num in self.Header.Num:
                    yield self.get(key, name, num)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.Values.shape}"

    def get(
        self,
        keywords: Union[Iterable[str], str] = None,
        names: Union[Iterable[str], str] = None,
        num: Union[Iterable[str], str] = None,
    ) -> SUMMARY:
        index = self.Header.index(keywords, names, num)
        new_df = self.Values[:, index]
        new_header = self.Header.new(index)
        return SUMMARY(self.CalcName, new_df, self.TimeVector, new_header)

    def get_group(self, key: str) -> SUMMARY:
        if key.lower() == "seg":
            index = self.Header.get_group_index("seg")
            return self.get_from_index(index)
        if key.lower() == "wel":
            index = self.Header.get_group_index("wel")
            return self.get_from_index(index)

    def get_from_index(self, index: np.ndarray) -> SUMMARY:
        new_df = self.Values[:, index]
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

    def to_time_series(self, method: str = None) -> TimeSeries:
        if method is None:
            if self.shape[1] != 1:
                raise ValueError
            return TimeSeries(self.TimeVector, self.Values.T[0])
        elif method == "sum":
            return TimeSeries(self.TimeVector, self.Values.sum(axis=1))
        else:
            raise KeyError

    def to_cum_time_series(self) -> CumTimeSeriasParam:
        if self.shape[1] != 1:
            raise ValueError
        return CumTimeSeriasParam(self.TimeVector, self.Values.T[0])

    def to_rate_time_series(
        self,
        method: str = "left",
        calc_method: str = None,
    ) -> RateTimeSeriasParam:
        if calc_method is None:
            if self.shape[1] != 1:
                raise ValueError
            return RateTimeSeriasParam(self.TimeVector, self.Values.T[0], method="left")
        elif calc_method == "sum":
            return RateTimeSeriasParam(
                self.TimeVector, self.Values.sum(axis=1), method="left"
            )
        else:
            raise KeyError

    @property
    def shape(self) -> Tuple[int, int]:
        i, j = self.Values.shape[0], self.Values.shape[1]
        return i, j

    def get_well_names(self) -> List[str]:
        return pd.unique(self.Header.well_name())

    def get_group_name(self) -> List[str]:
        return self.Header.group_name()

    def replace_name_from_df(
        self,
        old_wname: Iterable,
        new_wname: Iterable,
        old_sname: Iterable,
        new_sname: Iterable,
    ) -> SUMMARY:
        new = self
        new.Header.Num = self.Header.Num.astype(str)
        num = self.Header.Num.astype(str)
        name = self.Header.Names.astype(str)
        for ow, nw, os, ns in zip(old_wname, new_wname, old_sname, new_sname):
            new.Header.Names[(name == str(ow)) & (num == str(os))] = str(nw)
            new.Header.Num[(name == str(ow)) & (num == str(os))] = ns

        return new

    def replace_name_2(self, old_wname: Iterable, new_wname: Iterable) -> SUMMARY:
        new = deepcopy(self)
        new.Header.Num = self.Header.Num.astype(str)
        name = self.Header.Names.astype(str)
        for ow, nw in zip(old_wname, new_wname):
            new.Header.Names[name == str(ow)] = str(nw)
        return new

    def replace_name(
        self,
        obj_name: Dict[Union[str, int], Iterable[Union[str, int]]] = None,
        # num_name: Dict[Union[str, int], Iterable[Union[str, int]]] = None,
    ) -> SUMMARY:
        new_header = self.Header.replace_name(obj_name)
        return SUMMARY(self.CalcName, self.Values, self.TimeVector, new_header)

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
            target_value = self.Values[:, target_df.index.values]
            new_value = np.sum(target_value, axis=1)
            new.Values[:, rid] = new_value
            target_for_del = target_df[target_df.index.values != rid]
            for_del.extend(target_for_del.index.values)
            pass
        pattern = np.ones(self.Values.shape[1]).astype(bool)
        pattern[for_del] = False
        new.Values = new.Values[:, pattern]
        new.Header.Names = new.Header.Names[pattern]
        new.Header.Num = new.Header.Num[pattern]
        new.Header.Unit = new.Header.Unit[pattern]
        new.Header.Keywords = new.Header.Keywords[pattern]
        return new

    def split(
        self,
        well: Union[List[str], Tuple[str]] = None,
        bore: Union[List[str], Tuple[str]] = None,
        seg: Union[List[str], Tuple[str]] = None,
    ) -> FieldSUMMARY:

        fsummary = FieldSUMMARY(self.CalcName)

        for wname in self.get_well_names():
            all_well_summary = self.get(keywords=None, names=wname, num=None)

            if not (seg is None or bore is None or well is None):
                bore_summarys = []
                for bname in pd.unique(bore):
                    bore_seg = seg[bore == bname]
                    bore_data = all_well_summary.get(num=bore_seg)
                    bore_summarys.append(BoreSummary(bname, bore_data))
                wh_summary = WellHeadSUMMARY(all_well_summary.get_group("wel"))
                well_summary = WellSUMMARY(wname, wh_summary, bore_summarys, None)

            else:
                wh_summary = WellHeadSUMMARY(all_well_summary.get_group("wel"))
                s_summary = SegmentSUMMARY(all_well_summary.get_group("seg"))
                well_summary = WellSUMMARY(wname, wh_summary, None, s_summary)

            fsummary.append(well_summary)
        return fsummary


class FieldSUMMARY:
    def __init__(
        self,
        calc_name: str,
        wells: Optional[Iterable[WellSUMMARY]] = None,
        # group: Optional[Iterable[WellSUMMARY]] = None,
    ) -> None:
        self.CalcName = calc_name
        self.Wells: Dict[str, WellSUMMARY] = dict()
        if wells is not None:
            self.extend(wells)

        # if wells is not None:
        #     self.Group = list(group)
        # else:
        #     self.Group = []

    def __repr__(self) -> str:
        return self.CalcName

    def extend(self, values: Iterable[Union[WellSUMMARY]]) -> None:
        for val in values:
            self.append(val)

    def append(self, value: Union[WellSUMMARY]) -> None:
        if isinstance(value, WellSUMMARY):
            self.Wells[value.WellName] = value

    def choose_well(self, well_names: Iterable[str]) -> FieldSUMMARY:
        new = deepcopy(self)
        new_dict = dict()
        for wname in well_names:
            try:
                new_dict[str(wname)] = self.Wells[str(wname)]
            except KeyError:
                pass

        new.Wells = new_dict
        return new


class GroupSUMMARY:
    def __init__(self, data: SUMMARY) -> None:
        self.Data = data


class BoreSummary:
    def __init__(
        self,
        bore_name: Union[str, int],
        bore_summary: SUMMARY,
    ) -> None:
        self.Data = bore_summary
        self.BoreName = bore_name

    def __repr__(self) -> str:
        return str(self.BoreName)


class WellSUMMARY:
    def __init__(
        self,
        well_name: str,
        well_head_summary: WellHeadSUMMARY,
        bore_summary: Optional[Iterable[BoreSummary]] = None,
        segment_summary: Optional[SegmentSUMMARY] = None,
    ) -> None:
        self.WellHead = well_head_summary
        self.Segments = segment_summary
        self.WellName = well_name

        if bore_summary is not None:
            self.Bore: List[BoreSummary] = list(bore_summary)
        else:
            self.Bore = None

    def __repr__(self) -> str:
        return self.WellName

    def boring(
        self,
        bore: Union[List[str], Tuple[str]] = None,
        seg: Union[List[str], Tuple[str]] = None,
    ) -> None:
        pass
        if self.Segments is None:
            return None

        bore_summary = []
        for bname in pd.unique(bore):
            bore_seg = seg[bore == bname]
            bore_data = self.Segments.Data.get(num=bore_seg)
            bore_summary.append(BoreSummary(bname, bore_data))

        self.Bore = bore_summary
        self.Segments = None

    def __get_seg(self, seg_name: str) -> Optional[TimeSeries]:
        results = None
        if self.Segments is not None:
            seg_data = self.Segments.Data
            data = seg_data.get(keywords=seg_name)
            if results is None:
                results = data.to_time_series()
            else:
                results = results + data.to_time_series()

        if self.Bore is not None:
            for bore in self.Bore:
                seg_data = bore.Data
                data = seg_data.get(keywords=seg_name)
                if results is None:
                    results = data.to_time_series("sum")
                else:
                    results = results + data.to_time_series("sum")
        return results

    def __get_wel(self, w_param: Iterable[str]) -> Optional[TimeSeries]:
        results = None
        for param in w_param:
            if results is None:
                new = self.WellHead.Data.get(keywords=param)
                results = new.to_time_series()
            else:
                new_sum = self.WellHead.Data.get(keywords=param)
                new = new_sum.to_cum_time_series()
                results = results + new
        return results

    def normalize_segment_param(
        self,
        s_param: str,
        w_param: Union[Iterable[str], str],
    ) -> None:
        seg_param = self.__get_seg(s_param)
        if isinstance(w_param, Iterable):
            wel_param = self.__get_wel(w_param)
        else:
            wel_param = self.__get_wel([w_param])

        if seg_param is None:
            raise ValueError

        if wel_param is None:
            raise ValueError

        seg_param[seg_param.Data.values == 0] = 1

        if self.Segments is not None:
            seg = self.Segments.Data
            index = seg.Header.index(keywords=s_param)
            mylt = wel_param / seg_param
            seg.Values[:, index] = seg.Values[:, index] * abs(mylt.values)

        if self.Bore is not None:
            for bore in self.Bore:
                seg = bore.Data
                index = seg.Header.index(keywords=s_param)
                mylt = wel_param / seg_param
                for ind_seg in index:
                    seg.Values[:, ind_seg] = seg.Values[:, ind_seg] * abs(mylt.values)


class WellHeadSUMMARY:
    def __init__(self, data: SUMMARY) -> None:
        self.Data = data


class SegmentSUMMARY:
    def __init__(self, data: SUMMARY) -> None:
        self.Data = data


class SUMMARYList(list):
    pass
