from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from HydrodynamicUtilities.Models.DataFile import DataFile

import numpy as np

from HydrodynamicUtilities.Models.DataFile.ASCIIFile import ASCIIText
from HydrodynamicUtilities.Models.DataFile.Base import (
    ARITHMETIC,
    UnknownKeyword,
    Keyword,
    ArithmeticExpression,
)
from HydrodynamicUtilities.Models.DataFile.Sections import GRID


class BaseKeywordCreator:
    @staticmethod
    def create_arithmetic(data: str) -> ARITHMETIC:
        results = []
        for row in data.split("\n"):
            if "/" not in row:
                row = str(ASCIIText(row))
                results.append(ArithmeticExpression(row))
        return ARITHMETIC(results)

    @staticmethod
    def create_arrcube(data: str) -> GRID.ARRCube:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword(True))
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        return GRID.ARRCube(cubs, kw)

    def choose_fun(self, kw: str) -> Callable:
        return self.__getattribute__(kw.lower())

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = adata.get_keyword(False)
        if str(kw) == ARITHMETIC.__name__:
            adata.get_keyword(True)
            return self.create_arithmetic(str(adata))
        if str(kw)[:3] == "ARR":
            return self.create_arrcube(str(adata))
        else:
            return UnknownKeyword(str(kw), str(adata))