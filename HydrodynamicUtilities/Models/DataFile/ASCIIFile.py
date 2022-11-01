from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List, Tuple

from pathlib import Path
import pandas as pd
import numpy as np
import re
from ..Source.EtNKW_crutch import data as all_keyword


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

        df = pd.DataFrame(columns=())
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
        """
        data = re.subn(r"\d", "", self._Data, flags=re.ASCII)[0].upper()
        data = re.subn(r"--.*\n", "", data, flags=re.ASCII)[0]
        data = re.subn(r"\s", "", data, flags=re.ASCII)[0]
        data = re.subn(r"[.]", "", data, flags=re.ASCII)[0]
        data = re.subn(r"[*]", "", data, flags=re.ASCII)[0]
        """

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

        target = re.finditer(f"\n\s*[a-zA-Z]\w*\s", self._Data)
        for find in target:
            start = find.regs[0][0]
            end = find.regs[0][1]
            kword = self._Data[start: end].strip()
            if kword in all_keyword:
                results.append(start)
                keyword.append(kword)

        target = re.finditer(f"\n\s*ARR\w+\s", self._Data)
        for find in target:
            start = find.regs[0][0]
            end = find.regs[0][1]
            kword = self._Data[start: end].strip()
            results.append(start)
            keyword.append(kword)

        """
        for kword in all_keyword:
            if kword in data:
                target = re.finditer(f"\n\s*\S*\s", self._Data)
                kw_index = [x.regs[0][0] for x in target]
                results.extend(kw_index)
                keyword.extend([kword] * len(kw_index))

        for kword in ("ARR",):
            if kword in data:
                target = re.finditer(f"\n\s*{kword}", self._Data)
                kw_index = [x.regs[0][0] for x in target]
                results.extend(kw_index)
                keyword.extend([kword] * len(kw_index))
        """

        df = pd.DataFrame()
        df["ind"] = results
        df["kwd"] = keyword
        df = df.sort_values(by="ind", ignore_index=True)
        return df

    def _clean_arithmetic(self, df: pd.DataFrame) -> pd.DataFrame:
        arr_df = df[df["kwd"] == "ARITHMETIC"]

        if arr_df.empty:
            return df

        # for_del = np.zeros(df.shape).astype(bool)

        for rid, row in arr_df.iterrows():
            ind = row["ind"]
            slash_iter = re.finditer(f"/\s*\n", self._Data[ind:])
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


class ASCIIRow:
    def __init__(self, data: str) -> None:
        self.__data = data

    def __str__(self) -> str:
        return self.__data

    def strip_slash(self) -> ASCIIRow:
        # TODO
        data = self.__data
        return ASCIIRow(data)


class ASCIIText:
    def __init__(self, text: str) -> None:
        tt = text

        text = re.subn(r"--.*\n", "\n", text, flags=re.ASCII)[0]
        # text = re.subn(r"\n{2,}", "\n", text, flags=re.ASCII)[0]
        # text = re.subn(r"\n\s*\n", "\n", text, flags=re.ASCII)[0]
        text = re.subn(r"/\s*\n", "/\n", text, flags=re.ASCII)[0]

        text = text.strip()
        self.Text = text

    def __repr__(self) -> str:
        return self.Text[:100]

    def __str__(self) -> str:
        return self.Text

    def empty(self) -> bool:
        if self.Text == "":
            return True
        else:
            return False

    def __get_first_word(self) -> Tuple[int, int, str]:
        find = re.finditer(f"\s*[a-zA-Z]\w*\s*", self.Text, flags=re.ASCII).__next__()
        start = find.regs[0][0]
        end = find.regs[0][1]
        return start, end, self.Text[start:end].strip()

    def get_keyword(self, pop: bool = False) -> ASCIIRow:
        # TODO
        start, end, fw = self.__get_first_word()

        if fw in all_keyword:
            kw = fw
        elif fw[:3] == "ARR":
            kw = fw
        elif fw[:8] in all_keyword:
            kw = fw
        else:
            raise ValueError

        if pop:
            self.Text = self.Text[end:].strip()

        return ASCIIRow(kw)

    def get_first_word(self, pop: bool = False) -> ASCIIRow:
        values = []

        try:
            values.append(self.Text.index("\n"))
        except ValueError:
            pass

        try:
            values.append(self.Text.index("\t"))
        except ValueError:
            pass

        try:
            values.append(self.Text.index(" "))
        except ValueError:
            pass

        if values:
            min_ind = min(values)
        else:
            min_ind = -2

        results = self.Text[:min_ind]

        if pop:
            self.Text = self.Text[min_ind:]

        return ASCIIRow(results)

    def check_multiplication(self) -> bool:
        if "*" in self.Text:
            return True
        else:
            return False

    def replace_multiplication(self) -> ASCIIText:
        if not self.check_multiplication():
            return ASCIIText(self.Text)

        results = []
        for word in self.Text.split():
            if "*" in word:
                try:
                    value = word.split("*")[1]
                    if value == "":
                        value = "1*"
                    amount = int(word.split("*")[0])
                    reiteration = [value] * amount
                except IndexError:
                    amount = int(word.split("*")[0])
                    reiteration = ["1*"] * amount
                except ValueError:
                    reiteration = [word]
                results.extend(reiteration)

            else:
                results.append(word)

        return ASCIIText(" ".join(results))
        # return self

    def get_cub(self) -> np.ndarray:
        text = self.to_slash()

        if not text.check_multiplication():
            return np.array(text.split()).astype(float)

        results = []

        start_block = 0
        i = 0
        find = re.finditer(f"\s+\S+\*\S+\s*", self.Text, flags=re.ASCII)
        for string in find:
            start = string.regs[0][0]
            end = string.regs[0][1]
            word = self.Text[start:end].strip()
            if word == "2*0.2255":
                print(2*0.2255)
            if i == 47:
                print(i)
            split_word = word.split("*")
            string_word = int(split_word[0]) * f" {split_word[1]}"
            results.append(self.Text[start_block:start])
            results.append(string_word)
            start_block = end - 1
            i += 1

        string_results = " ".join(results)
        return np.array(string_results.split(), dtype=float)

    def to_slash(self, pop: bool = False, end_slash: bool = False) -> ASCIIText:
        if end_slash:
            ind = self.Text.find("/\n")
        else:
            ind = self.Text.find("/")

        text = self.Text[: ind + 1]

        if pop:
            self.Text = self.Text[ind + 1 :].strip()

        return ASCIIText(text[:-1])

    def del_slash(self) -> ASCIIText:
        return ASCIIText(self.Text.replace("/", "").strip())

    def split(self) -> List[str]:
        return self.Text.split()
