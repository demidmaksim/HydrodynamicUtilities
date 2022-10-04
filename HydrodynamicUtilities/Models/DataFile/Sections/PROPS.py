from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import List, Dict, Type, Tuple, Any
    from ..Base import DataFile

import numpy as np

from copy import deepcopy

from ..Base import Section, Keyword, BaseKeywordCreator, UnknownKeyword, ARITHMETIC
from ..ASCIIFile import ASCIIText


class DENSITY(Keyword):
    __Order = {
        "oil": 600.0,
        "water": 999.014,
        "gas": 1,
    }

    def __init__(self):
        pass


class PVTO(Keyword):
    def __init__(
        self,
        gor: np.array,
        pressure: np.array,
        expansion_coefficient: np.array,
        viscosity: np.array,
    ):
        self.GOR = gor
        self.Pressure = pressure
        self.Expansion = expansion_coefficient
        self.Viscosity = viscosity


class LETGOModel(Keyword):

    __Order = {
        "sgl": 0,
        "sgu": 1,
        "sgcr": 0,
        "sogcr": 0,
        "krolg": 1,
        "krorg": 1,
        "krgr": None,
        "krgu": None,
        "pcog": 0,
        "nog": 4,
        "ng": 4,
        "npg": 4,
        "spcg": -1,
        "tg": 2,
        "eg": 1,
        "tog": 2,
        "eog": 1,
    }

    def __init__(
        self,
        sgl: float = 0,
        sgu: float = 1,
        sgcr: float = 0,
        sogcr: float = 0,
        krolg: float = 1,
        krorg: float = 1,
        krgr: float = None,
        krgu: float = None,
        pcog: float = 0,
        nog: float = 4,
        ng: float = 4,
        npg: float = 4,
        spcg: float = -1,
        tg: float = 2,
        eg: float = 1,
        tog: float = 2,
        eog: float = 1,
    ) -> None:
        self.SGL = sgl
        self.SGU = sgu
        self.SGCR = sgcr
        self.SOGCR = sogcr
        self.KROLG = krolg
        self.KRORG = krorg
        self.KRGR = krgr
        self.KRGU = krgu
        self.PCOG = pcog
        self.NOG = nog
        self.NG = ng
        self.NPG = npg
        self.SPCG = spcg
        self.TG = tg
        self.EG = eg
        self.TOG = tog
        self.EOG = eog

    @classmethod
    def get_base_value(cls) -> Dict[str, Any]:
        return deepcopy(cls.__Order)


class LETGO(Keyword):
    def __init__(self, data: List[LETGOModel] = None) -> None:
        if data is not None:
            self.Data = data
        else:
            self.Data = list()

    def append(self, model: LETGOModel) -> None:
        self.Data.append(model)


class FluidPVTModel:
    def __init__(self) -> None:
        pass


class RockModel:
    def __init__(self) -> None:
        pass


class Other:
    def __init__(self) -> None:
        pass

    def __setattr__(self, key: str, value: Any) -> None:
        if isinstance(value, ARITHMETIC):
            if hasattr(self, "ARITHMETIC"):
                arithmetic = self.ARITHMETIC
                arithmetic = arithmetic + value
                super().__setattr__(key, arithmetic)
            else:
                super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)


class FluidPVTModelConstructor(BaseKeywordCreator):
    def pvto(self, data: ASCIIText) -> PVTO:
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
        return PVTO(
            gor.astype(float),
            pressure.astype(float),
            expansion.astype(float),
            viscosity.astype(float),
        )

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in PROPS.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        adata = adata.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)


class RockModelConstructor(BaseKeywordCreator):
    def letgo(self, data: ASCIIText) -> LETGO:
        results = LETGO()
        while not data.empty():
            string = data.to_slash(True)
            if string.empty():
                break
            string = string.replace_multiplication()
            value = string.split()
            pattern = LETGOModel.get_base_value()
            for pid, pos in enumerate(pattern.keys()):
                if len(value) < pid:
                    break
                pattern[pos] = value[pid]
            results.append(LETGOModel(**pattern))
        return results

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in PROPS.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        adata = adata.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)


class PROPSConstructor(BaseKeywordCreator):
    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword())

        if str(kw) in PROPS.get_fluid_keyword():
            return FluidPVTModelConstructor().create(str(adata), data_file)
        elif str(kw) in PROPS.get_rock_keyword():
            return RockModelConstructor().create(str(adata), data_file)

        else:
            kw = adata.get_keyword(True)
            return super().create(data, data_file)


class PROPS(Section):
    __Keyword = {
        "LETGO": LETGO,
        "PVTO": PVTO,
    }

    __Fluid = ("PVTO",)

    __Rock = ("LETGO",)

    def __init__(self, data_file: DataFile):
        super().__init__(data_file)
        self.Fluid = FluidPVTModel()
        self.Rock = RockModel()
        self.Other = Other()

    def __setattr__(self, key, value) -> None:
        if isinstance(value, Keyword):
            kw = value.__repr__()
            if kw in self.__Fluid:
                self.Fluid.__setattr__(kw, value)
            elif kw in self.__Rock:
                self.Rock.__setattr__(kw, value)
            else:
                self.Other.__setattr__(kw, value)
        elif isinstance(value, str):
            super().__setattr__(key, ASCIIText(value))
        else:
            super().__setattr__(key, value)

    @classmethod
    def get_constructor(cls) -> Type[BaseKeywordCreator]:
        return PROPSConstructor

    @classmethod
    def get_famous_keyword(self) -> Dict[str, Type[Keyword]]:
        return self.__Keyword

    @classmethod
    def get_fluid_keyword(cls) -> Tuple[str, ...]:
        return cls.__Fluid

    @classmethod
    def get_rock_keyword(cls) -> Tuple[str, ...]:
        return cls.__Rock
