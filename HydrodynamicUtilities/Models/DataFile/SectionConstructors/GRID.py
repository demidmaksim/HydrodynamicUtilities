from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import DataFile

import numpy as np

from typing import Type

from HydrodynamicUtilities.Models.DataFile.Base import Keyword, UnknownKeyword
from HydrodynamicUtilities.Models.DataFile.ASCIIFile import ASCIIText
from HydrodynamicUtilities.Models.DataFile.Sections import GRID
from HydrodynamicUtilities.Reader.ASCIIDataFileReader.BaseCreator import BaseKeywordCreator
import time


class SettingConstructor(BaseKeywordCreator):
    @staticmethod
    def init(*args, **kwargs) -> GRID.INIT:
        return GRID.INIT(*args, **kwargs)

    def create_settings(self, data: ASCIIText, kw: str) -> Keyword:
        if str(kw) not in GRID.GRID.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(data))

        adata = data.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = str(adata.get_keyword(True))
        return self.create_settings(adata, kw)


class CubsConstructor(BaseKeywordCreator):
    @staticmethod
    def create_cubs(data: ASCIIText, kw: str):
        t = time.time()
        cubs = data.get_cub()
        print(time.time() - t)
        """
        data = data.replace_multiplication()
        data = data.to_slash()
        cubs = np.array(data.split(), dtype=float)
        """
        famous_keyword = GRID.Cubs.get_famous_keyword()
        keyword_class: Type[GRID.CubeProperty] = famous_keyword[kw]
        return keyword_class(cubs)

    def create(self, data: str, data_file: DataFile) -> GRID.CubeProperty:
        adata = ASCIIText(data)
        kw = str(adata.get_keyword(True))
        return self.create_cubs(adata, kw)


class MeshConstructor(BaseKeywordCreator):
    @staticmethod
    def create_mesh_keyword(adata: ASCIIText, kw: str):
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        famous_keyword = GRID.GRID.get_famous_keyword()
        keyword_class: Type[Keyword] = famous_keyword[kw]
        return keyword_class(data=cubs)

    @classmethod
    def create(cls, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = str(adata.get_keyword(True))
        return cls.create_mesh_keyword(adata, kw)


class GRIDConstructor(BaseKeywordCreator):
    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = str(adata.get_keyword(True))

        if str(kw) in GRID.GRID.get_mesh_keyword():
            return MeshConstructor().create_mesh_keyword(adata, kw)
        elif str(kw) in GRID.GRID.get_cubs_keyword():
            return CubsConstructor().create_cubs(adata, kw)
        elif "ARR" == str(kw)[:3]:
            return CubsConstructor().create_arrcube(adata, kw)
        elif str(kw) not in GRID.GRID.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))
        else:
            return SettingConstructor().create_settings(adata, kw)
