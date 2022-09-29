from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

from pathlib import Path
import pandas as pd
import numpy as np
import re
import time

from HydrodynamicUtilities.Models.Source.EtNKW_crutch import data as all_keyword


class ASCIIFile:
    def __init__(
        self,
        path: Path,
        name: str = None,
        parent: Optional[ASCIIFile] = None,
        main_path: Path = None,
    ) -> None:
        self.Path = path
        self.Parent = parent
        self.MainPath = main_path
        self.AttachedFiles = list()
        self.set_name(name)
        self.read_file(path)
        self.Indexes = self.indexing()
        self.read_attached_files()

    def __repr__(self) -> str:
        return self.Name

    def read_file(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as file:
            self.Data = file.read()

    def set_name(self, name: str) -> None:
        if name is None:
            self.Name = str(Path)
        else:
            self.Name = name

    def read_attached_files(self) -> None:

        if self.MainPath is None:
            main_path = self.Path
        else:
            main_path = self.MainPath

        for path in self.read_include():
            name = str(path).split(str(main_path.parent))[-1]
            new_data = ASCIIFile(path, name, self, main_path)
            self.AttachedFiles.append(new_data)

    def indexing(self) -> pd.DataFrame:
        t = time.time()
        kw = list()
        ind = list()
        data = self.Data.split("\n")
        i = 0
        # self.Data[list(re.finditer(r"PERMX", self.Data))[0].regs[0][0]:list(re.finditer(r"PERMX", self.Data))[0].regs[0][1]]
        while data:
            line = data.pop(0)

            if not line.split():
                pass
            elif "ARITHMETIC" in line.upper():
                kw.append("ARITHMETIC")
                ind.append(i)
                while data:
                    line = data.pop(0)
                    if line.strip() == "/":
                        i += 1
                        break
                    i += 1
            elif line.strip().split()[0] in all_keyword:
                kw.append(line.split()[0])
                ind.append(i)
            elif line.strip()[:8] in all_keyword:
                kw.append(line.split()[:8])
                ind.append(i)

            i += 1

        df = pd.DataFrame()
        df["Line"] = ind
        df["Keyword"] = kw
        df = df.sort_values("Line")
        values = np.zeros(df["Line"].values.shape) * np.NAN
        values[:-1] = df["Line"].iloc[1:].values
        df["end_line"] = values
        # df["Path"] = self.Path
        print(f"{self.Path}\tindexing: {round(time.time() - t, 2)}")
        return df

    def read_include(self) -> List[Path]:
        df = self.Indexes
        if df.empty:
            return []

        if df is None:
            df = self.indexing()
        df = df.sort_values("Line")

        target = df[df["Keyword"] == "INCLUDE"]
        lines = self.Data.split("\n")
        attached_files = list()
        for rid, row in target.iterrows():
            start = row["Line"]
            end = row["end_line"]
            if pd.isna(end):
                data = lines[start:]
            else:
                data = lines[start : int(end)]
            string = "\n".join(data)
            if self.MainPath is None:
                new_path = self.Path.parent / get_path(string)
            else:
                new_path = self.MainPath.parent / get_path(string)
            attached_files.append(new_path)
        return attached_files

    def passing(self):
        pass

    def convert_to(self):
        pass


class ASCIIFileTest(ASCIIFile):
    def __init__(
        self,
        path: Path,
        name: str = None,
        parent: Optional[ASCIIFile] = None,
        main_path: Path = None,
    ):
        super().__init__(path, name, parent, main_path)
        # self.reindex()
        # self.research()
        # self.research_2()
        # self.research_3()
        self.research_4()

    def read_attached_files(self) -> None:

        if self.MainPath is None:
            main_path = self.Path
        else:
            main_path = self.MainPath

        for path in self.read_include():
            name = str(path).split(str(main_path.parent))[-1]
            new_data = ASCIIFileTest(path, name, self, main_path)
            self.AttachedFiles.append(new_data)

    def research_4(self) -> None:
        t = time.time()
        data = re.subn(
            r"\d",
            "",
            self.Data,
        )[0].upper()
        data = re.subn(r"--.*\n", "", data, flags=re.ASCII)[0]
        data = re.subn(r"\s", "", data, flags=re.ASCII)[0]
        data = re.subn(r"[.]", "", data, flags=re.ASCII)[0]
        data = re.subn(r"[*]", "", data, flags=re.ASCII)[0]

        results = []

        for kword in all_keyword:
            if kword in data:
                target = re.finditer(r"" + kword, self.Data, flags=re.ASCII)
                r = list(target)

        print(f"{self.Path}\tresearch_4: {round(time.time() - t, 2)}")

    def research_3(self) -> None:
        t = time.time()
        data = re.subn(r"\d", "", self.Data)[0]
        data = re.subn(r"\s", "", data)

        for kword in all_keyword:
            if kword in data:
                res = list(re.finditer(r"" + kword, self.Data))
                data = [x.regs[0][0] for x in res]

        print(f"{self.Path}\tresearch_3: {round(time.time() - t, 2)}")

    def research_2(self) -> None:
        t = time.time()
        data = re.subn(r"\d", "", self.Data)[0]
        data = re.subn(r"\s", "", data)

        for kword in all_keyword:
            if kword in data:
                list(re.finditer(r"" + kword, self.Data))
        print(f"{self.Path}\tresearch_2: {round(time.time() - t, 2)}")

    def research(self) -> None:
        t = time.time()
        data = re.subn(r"\d", "", self.Data)

        for kword in all_keyword:
            if kword in data:
                list(re.finditer(r"" + kword, self.Data))
        print(f"{self.Path}\tresearch: {round(time.time() - t, 2)}")

    def reindex(self) -> None:
        t = time.time()
        for kword in all_keyword:
            list(re.finditer(r"" + kword, self.Data))
        print(f"{self.Path}\treindex: {round(time.time() - t, 2)}")
