from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import DataFile

import numpy as np


from HydrodynamicUtilities.Models.DataFile.Base import Keyword, UnknownKeyword
from HydrodynamicUtilities.Models.DataFile.ASCIIFile import ASCIIText
from HydrodynamicUtilities.Models.DataFile.Sections import PROPS
from HydrodynamicUtilities.Reader.ASCIIDataFileReader.BaseCreator import BaseKeywordCreator


class FluidPVTModelConstructor(BaseKeywordCreator):
    @staticmethod
    def pvto(data: ASCIIText) -> PROPS.PVTO:
        gor = np.array([])
        pressure = np.array([])
        expansion = np.array([])
        viscosity = np.array([])
        while not data.empty():
            block = data.to_slash(True)
            if block.empty():
                break
            block_list = block.split()
            gor_point = block_list.pop(0)
            pressure = np.concatenate((pressure, block_list[0::3]))
            expansion = np.concatenate((expansion, block_list[1::3]))
            viscosity = np.concatenate((viscosity, block_list[2::3]))
            gor = np.concatenate((gor, [gor_point] * int(len(block_list) / 3)))
        return PROPS.PVTO(
            gor.astype(float),
            pressure.astype(float),
            expansion.astype(float),
            viscosity.astype(float),
        )

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in PROPS.PROPS.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        adata = adata.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)


class RockModelConstructor(BaseKeywordCreator):
    @staticmethod
    def letgo(data: ASCIIText) -> PROPS.LETGO:
        results = PROPS.LETGO()
        while not data.empty():
            string = data.to_slash(True)
            if string.empty():
                break
            string = string.replace_multiplication()
            value = string.split()
            pattern = PROPS.LETGOModel.get_base_value()
            for pid, pos in enumerate(pattern.keys()):
                if len(value) < pid:
                    break
                pattern[pos] = value[pid]
            results.append(PROPS.LETGOModel(**pattern))
        return results

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in PROPS.PROPS.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        adata = adata.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)


class PROPSConstructor(BaseKeywordCreator):
    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword())

        if str(kw) in PROPS.PROPS.get_fluid_keyword():
            return FluidPVTModelConstructor().create(str(adata), data_file)
        elif str(kw) in PROPS.PROPS.get_rock_keyword():
            return RockModelConstructor().create(str(adata), data_file)

        else:
            # kw = adata.get_keyword(True)
            return super().create(data, data_file)
