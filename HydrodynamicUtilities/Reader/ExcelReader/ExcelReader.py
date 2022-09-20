from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, List, Tuple
    from pathlib import Path

    ListOfPath = Union[List[Union[str, Path]], Tuple[Union[str, Path], ...]]

import pandas as pd
from pathlib import Path

from multiprocessing import Pool


from HydrodynamicUtilities.Models.ExcelFile import (
    RawExcelFile,
    RawExcelDataDict,
    RawExcelSheet,
)
import time

"""
def test(path: Union[Path, str]) -> RawExcelFile:
    if type(path) == str:
        path = Path(path)

    try:
        df = pd.read_excel(
            io=path,
            sheet_name=None,
            header=None,
            # skiprows=(2,),
            engine="pyxlsb",
            na_values=(" ",),
        )

        results = dict()
        for sname, sheet in df.items():
            results[sname] = RawExcelSheet(sheet, sname)

        return RawExcelFile(results, path)

    except KeyError:
        df = pd.read_excel(
            io=path,
            sheet_name=None,
            header=None,
            # skiprows=(2,),
            engine="openpyxl",
            na_values=(" ",),
        )

        results = dict()
        for sname, sheet in df.items():
            results[sname] = RawExcelSheet(sheet, sname)

        return RawExcelFile(results, path)
"""


class BaseReader:
    @staticmethod
    def log(path: str, time: str) -> None:
        print(path, time)

    @staticmethod
    def _read_one_excel_file(path: Union[Path, str]) -> RawExcelFile:
        if type(path) == str:
            path = Path(path)

        try:
            df = pd.read_excel(
                io=path,
                sheet_name=None,
                header=None,
                # skiprows=(2,),
                engine="pyxlsb",
                na_values=(" ",),
            )

            results = dict()
            for sname, sheet in df.items():
                results[sname] = RawExcelSheet(sheet, sname)

            return RawExcelFile(results, path)

        except KeyError:
            df = pd.read_excel(
                io=path,
                sheet_name=None,
                header=None,
                # skiprows=(2,),
                engine="openpyxl",
                na_values=(" ",),
            )

            results = dict()
            for sname, sheet in df.items():
                results[sname] = RawExcelSheet(sheet, sname)

            return RawExcelFile(results, path)

    @classmethod
    def __read_many_excel_files(
        cls,
        list_of_path: ListOfPath,
        multiprocessing: bool,
    ) -> RawExcelDataDict:
        if multiprocessing:
            return cls.__multi_read_many_excel_files(list_of_path)
        else:
            return cls.__single_read_many_excel_files(list_of_path)

    @classmethod
    def __single_read_many_excel_files(
        cls,
        list_of_path: ListOfPath,
    ) -> RawExcelDataDict:
        redd = RawExcelDataDict()
        for path in list_of_path:
            t = time.time()
            redd.append(cls._read_one_excel_file(path))
            cls.log(str(path), str(round(time.time() - t, 2)))
        return redd

    @classmethod
    def __multi_read_many_excel_files(
        cls,
        list_of_path: ListOfPath,
    ) -> RawExcelDataDict:
        results = RawExcelDataDict()

        with Pool(len(list_of_path)) as p:

            answer = list(p.map(cls._read_one_excel_file, list_of_path))
            results.extend(answer)

        return results

    @classmethod
    def read_excel_files(
        cls,
        path: Union[ListOfPath, Union[str, Path]],
        multiprocessing: bool = False,
    ) -> RawExcelDataDict:
        if type(path) in (list, tuple):
            return cls.__read_many_excel_files(path, multiprocessing)
        elif type(path) == str:
            return cls.__read_many_excel_files([path], multiprocessing)
        elif issubclass(type(path), Path):
            return cls.__read_many_excel_files([path], multiprocessing)
        else:
            raise TypeError()
