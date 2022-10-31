from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import DataFile

import numpy as np

from typing import Type

from HydrodynamicUtilities.Models.DataFile.Base import Keyword, UnknownKeyword
from HydrodynamicUtilities.Models.DataFile.ASCIIFile import ASCIIText
from HydrodynamicUtilities.Models.DataFile.Sections import GRID
from ..BaseCreator import BaseKeywordCreator


class SettingConstructor(BaseKeywordCreator):
    @staticmethod
    def init(*args, **kwargs) -> GRID.INIT:
        return GRID.INIT(*args, **kwargs)

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in GRID.GRID.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        adata = adata.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)


class CubsConstructor(BaseKeywordCreator):
    def create(self, data: str, data_file: DataFile) -> GRID.CubeProperty:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword(True))
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        famous_keyword = GRID.Cubs.get_famous_keyword()
        keyword_class: Type[GRID.CubeProperty] = famous_keyword[kw]
        return keyword_class(cubs)


class MeshConstructor(BaseKeywordCreator):
    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword(True))
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        famous_keyword = GRID.GRID.get_famous_keyword()
        keyword_class: Type[Keyword] = famous_keyword[kw]
        return keyword_class(data=cubs)


class GRIDConstructor(BaseKeywordCreator):
    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword())

        if str(kw) in GRID.GRID.get_mesh_keyword():
            return MeshConstructor().create(str(adata), data_file)
        elif str(kw) in GRID.GRID.get_cubs_keyword():
            return CubsConstructor().create(str(adata), data_file)
        elif "ARR" == str(kw)[:3]:
            return CubsConstructor().create_arrcube(str(adata))
        elif str(kw) not in GRID.GRID.get_famous_keyword().keys():
            kw = adata.get_keyword(True)
            return UnknownKeyword(str(kw), str(adata))
        else:
            return SettingConstructor().create(str(adata), data_file)
