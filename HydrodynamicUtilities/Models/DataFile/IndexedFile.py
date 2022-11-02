from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

from pathlib import Path
import pandas as pd
import numpy as np
import re
from ..Source.EtNKW_crutch import data as all_keyword
from .SectionConstructors import get_constructor


class LineIndexes:
    def __init__(self):
        self.ID = []
        self.KeyWord = []

    def __repr__(self) -> str:
        return f"LineIndexes {len(self.KeyWord)}"

    def append(self, ind: int, keyword):
        self.ID.append(ind)
        self.KeyWord.append(keyword)

    def check_(self) -> None:
        pass

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        if not self.ID:
            return None

        df = pd.DataFrame()
        df["start"] = self.ID
        df["finish"] = self.ID[1:] + [-1]
        df["keyword"] = self.KeyWord
        value = np.zeros(len(self.KeyWord))
        value[df["keyword"] == "INCLUDE"] = 1
        df["include"] = value.cumsum()
        df = df.sort_values("start")
        return df


class ASCIIFilesIndexer:
    _all_keyword = all_keyword

    def __init__(
        self,
        path: Path,
        parent: Optional[ASCIIFilesIndexer] = None,
        child_entities: List[ASCIIFilesIndexer] = None,
    ) -> None:
        self.Path = path
        self.Parent = parent
        if child_entities is None:
            self.Entities = []
        else:
            self.Entities = child_entities
        self._set_relative_name()
        self._read_file(self.Path)
        self._indexing()

    def __repr__(self) -> str:
        if self.Parent is None:
            return str(self.Path)
        else:
            return str(self._get_relative_name())

    def _get_main_path(self, folder: bool) -> Path:
        target_object = self
        while target_object.Parent is not None:
            target_object = target_object.Parent
        if folder:
            return Path(target_object.Path.parent)
        else:
            return target_object.Path

    def _get_relative_name(self) -> Path:
        target_object = self
        while target_object.Parent is not None:
            target_object = target_object.Parent
        if target_object != self:
            main_path = target_object.Path.parent
            return Path(str(self.Path).split(str(main_path))[1])
        else:
            return Path("")

    def _set_relative_name(self) -> None:
        target_object = self
        while target_object.Parent is not None:
            target_object = target_object.Parent
        if target_object != self:
            main_path = target_object.Path.parent
            self._RelativeName = str(self.Path).split(str(main_path))[1]

    def _read_file(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as file:
            self._Data = file.read().upper()

    def _keyword_indexing(self) -> pd.DataFrame:

        results = []
        keyword = []

        f_line = self._Data[: self._Data.find("\n")]
        if f_line != "":
            if f_line.split()[0] in all_keyword:
                results.append(0)
                keyword.append(f_line.split()[0])
            elif f_line[:8] in all_keyword:
                results.append(0)
                keyword.append(f_line[:8])

        target = re.finditer(r"\n\s*[a-zA-Z]\w*\s", self._Data)
        for find in target:
            start = find.regs[0][0]
            end = find.regs[0][1]
            kword = self._Data[start:end].strip()
            if kword in all_keyword:
                results.append(start)
                keyword.append(kword)
            elif kword[:3] == "ARR":
                results.append(start)
                keyword.append(kword)

        df = pd.DataFrame()
        df["ind"] = results
        df["kwd"] = keyword
        df = df.sort_values(by="ind", ignore_index=True)
        return df

    def _clean_arithmetic(self, df: pd.DataFrame) -> pd.DataFrame:
        arr_df = df[df["kwd"] == "ARITHMETIC"]

        if arr_df.empty:
            return df

        for rid, row in arr_df.iterrows():
            ind = row["ind"]
            slash_iter = re.finditer(r"/\s*\n", self._Data[ind:])
            slash_ind = slash_iter.__next__().regs[0][0] + ind
            next_kw = df["ind"].loc[rid + 1]
            if next_kw < slash_ind:
                pattern = (df["ind"] > ind) & (df["ind"] < slash_ind)
                df = df[~pattern]
        return df

    def _indexing(self) -> None:
        self.Indexes = LineIndexes()
        df = self._keyword_indexing()
        df = self._clean_arithmetic(df)
        df = df.sort_values("ind")
        self.Indexes.ID = (df["ind"]).to_list()
        self.Indexes.KeyWord = df["kwd"].to_list()

    @staticmethod
    def _get_path(string: str) -> Path:
        if "'" in string:
            target_latter = "'"
        elif '"' in string:
            target_latter = '"'
        else:
            target_latter = None

        if target_latter is None:
            return Path(string.split()[1])
        else:
            source = string.split()[1]
            ind_f = source.index(target_latter)
            ind_s = source.index(target_latter, ind_f + 1)
            return Path(source[ind_f + 1 : ind_s])

    def get_path(self) -> List[Path]:
        results = []
        df = self.Indexes.get_dataframe()
        if df is None:
            return []

        df = df[df["keyword"] == "INCLUDE"]
        for rid, row in df.iterrows():
            start = row["start"]
            finish = row["finish"]
            text = self._Data[start:finish]
            path = self._get_main_path(True) / self._get_path(text)
            results.append(path)
        return results

    def get_text(self) -> str:
        return self._Data
