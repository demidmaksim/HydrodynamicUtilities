from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Base import DataFile
    from typing import Type, Dict, Tuple, Union, Optional, Any
    from .RUNSPEC import DIMENS

import numpy as np

from ..Base import Section, UnInitializedSection, Keyword, UnknownKeyword
from ..ASCIIFile import ASCIIText


class CubeProperty(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data

    def __add__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data + other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data + other.Data)
        else:
            raise TypeError

    def __sub__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data - other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data - other.Data)
        else:
            raise TypeError

    def __mul__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data * other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data * other.Data)
        else:
            raise TypeError

    def __floordiv__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data // other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data // other.Data)
        else:
            raise TypeError

    def __div__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data / other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data / other.Data)
        else:
            raise TypeError

    def __truediv__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data / other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data / other.Data)
        else:
            raise TypeError

    def __mod__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data % other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data % other.Data)
        else:
            raise TypeError

    def __divmod__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> Tuple[CubeProperty, CubeProperty]:
        if isinstance(other, (int, float, np.ndarray)):
            integral = CubeProperty(self.Data // other)
            remainder = CubeProperty(self.Data % other)
            return integral, remainder
        elif isinstance(other, CubeProperty):
            integral = CubeProperty(self.Data // other.Data)
            remainder = CubeProperty(self.Data % other.Data)
            return integral, remainder
        else:
            raise TypeError

    def __pow__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data ** other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data ** other.Data)
        else:
            raise TypeError

    def __radd__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other + self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data + self.Data)
        else:
            raise TypeError

    def __rsub__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other - self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data - self.Data)
        else:
            raise TypeError

    def __rmul__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other * self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data * self.Data)
        else:
            raise TypeError

    def __rfloordiv__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other // self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data // self.Data)
        else:
            raise TypeError

    def __rdiv__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other / self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data / self.Data)
        else:
            raise TypeError

    def __rtruediv__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other / self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data / self.Data)
        else:
            raise TypeError

    def __rmod__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other % self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data % self.Data)
        else:
            raise TypeError

    def __rdivmod__(
        self,
        other: Union[int, float, np.ndarray, CubeProperty],
    ) -> Tuple[CubeProperty, CubeProperty]:
        if isinstance(other, (int, float, np.ndarray)):
            integral = CubeProperty(other // self.Data)
            remainder = CubeProperty(other % self.Data)
            return integral, remainder
        elif isinstance(other, CubeProperty):
            integral = CubeProperty(other.Data // self.Data)
            remainder = CubeProperty(other.Data % self.Data)
            return integral, remainder
        else:
            raise TypeError

    def __rpow__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(other ** self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data ** self.Data)
        else:
            raise TypeError


class ARRCube(CubeProperty):
    def __init__(self, data: np.ndarray, name: str) -> None:
        super().__init__(data)
        self.Name = name

    def __repr__(self) -> str:
        return self.Name


class PORO(CubeProperty):
    pass


class PERMX(CubeProperty):
    pass


class PERMY(CubeProperty):
    pass


class PERMZ(CubeProperty):
    pass


class ACTNUM(CubeProperty):
    pass


class INIT(Keyword):
    pass


class COORD(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class FILHEAD(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class GRIDHEAD(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class GRIDUNIT(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class MAPAXES(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class MAPUNIT(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class ZCORN(Keyword):
    def __init__(self, data: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data


class Mesh:
    def __init__(self, section: GRID) -> None:
        self.Section = section

    def __setattr__(self, key, value) -> None:
        if isinstance(value, str):
            super().__setattr__(key, ASCIIText(value))
        elif isinstance(value, Keyword):
            value.ParentSection = self
            super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)


class Cubs:
    def __init__(self, section: GRID) -> None:
        self.__Section = section

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __setattr__(self, key, value) -> None:
        if isinstance(value, CubeProperty):
            value.ParentSection = self.__Section
            super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)

    def get_section(self) -> Section:
        return self.__Section

    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[CubeProperty]]:
        cub_kw = GRID.get_cubs_keyword()
        fkw = GRID.get_famous_keyword()
        results = {kw: fkw[kw] for kw in cub_kw}
        return results

    def get_cubs(self) -> Dict[str, CubeProperty]:
        results = dict()
        for kw in self.__dir__():
            if kw in GRID.get_cubs_keyword():
                results[kw] = self.__getattribute__(kw)
        return results


class Setting:
    def __init__(self, section: GRID) -> None:
        self.Section = section

    def __setattr__(self, key, value) -> None:
        if isinstance(value, str):
            super().__setattr__(key, ASCIIText(value))
        elif isinstance(value, Keyword):
            value.ParentSection = self
            super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)


class Other:
    def __init__(self, section: GRID) -> None:
        self.Section = section

    def __setattr__(self, key, value) -> None:
        if isinstance(value, str):
            super().__setattr__(key, ASCIIText(value))
        elif isinstance(value, Keyword):
            value.ParentSection = self
            super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)


class GRID(Section):
    __Keyword = {
        "PORO": PORO,
        "PERMX": PERMX,
        "PERMY": PERMY,
        "PERMZ": PERMZ,
        "ACTNUM": ACTNUM,
        "COORD": COORD,
        "FILHEAD": FILHEAD,
        "GRIDHEAD": GRIDHEAD,
        "GRIDUNIT": GRIDUNIT,
        "MAPAXES": MAPAXES,
        "MAPUNIT": MAPUNIT,
        "ZCORN": ZCORN,
        "INIT": INIT,
    }

    __Mesh = (
        "COORD",
        "ZCORN",
    )

    __Cubs = (
        "PORO",
        "PERMX",
        "PERMY",
        "PERMZ",
        "ACTNUM",
    )

    __Setting = ("INIT",)

    __FamousKeyword = tuple(__Keyword.keys())

    def __init__(self, data_file: DataFile) -> None:
        super().__init__(data_file)
        self.Grid = Mesh(self)
        self.Cubs = Cubs(self)
        self.Setting = Setting(self)
        self.Other = Other(self)

    def __setattr__(self, key, value) -> None:
        if isinstance(value, Keyword):
            kw = value.__repr__()
            if kw in self.__Mesh:
                self.Grid.__setattr__(kw, value)
            elif kw in self.__Cubs:
                self.Cubs.__setattr__(kw, value)
            elif kw in self.__Setting:
                self.Setting.__setattr__(kw, value)
            elif "ARR" == kw[:3]:
                self.Cubs.__setattr__(kw, value)
            else:
                self.Other.__setattr__(key, value)
        elif isinstance(value, str):
            self.Other.__setattr__(key, ASCIIText(value))
        else:
            super().__setattr__(key, value)

    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return cls.__Keyword

    @classmethod
    def get_setting_keyword(cls) -> Tuple[str, ...]:
        return cls.__Setting

    @classmethod
    def get_mesh_keyword(cls) -> Tuple[str, ...]:
        return cls.__Mesh

    @classmethod
    def get_cubs_keyword(cls) -> Tuple[str, ...]:
        return cls.__Cubs

    def __for_index(self) -> Optional[Tuple[DIMENS, CubeProperty]]:
        datafile = self.get_data_file()
        try:
            dimens = datafile.RUNSPEC.DIMENS
        except AttributeError:
            return None

        try:
            kw_name = list(self.Cubs.__dict__.keys())[0]
            kw: CubeProperty = getattr(self.Cubs, kw_name)
        except AttributeError:
            return None
        return dimens, kw

    def get_k_index(self) -> Optional[CubeProperty]:
        dc = self.__for_index()
        if dc is None:
            return None

        dimens, kw = dc[0], dc[1]

        index = np.arange(len(kw.Data))
        k_index = index // (dimens.NX * dimens.NY) + 1
        return CubeProperty(k_index, section=self)

    def get_j_index(self) -> Optional[CubeProperty]:
        dc = self.__for_index()
        if dc is None:
            return None

        dimens, kw = dc[0], dc[1]

        index = np.arange(len(kw.Data))
        k_index = index // (dimens.NX * dimens.NY) + 1
        layer_index = (k_index - 1) * dimens.NX * dimens.NY
        j_index = layer_index // dimens.NX
        return CubeProperty(j_index, section=self)

    def get_i_index(self) -> Optional[CubeProperty]:
        dc = self.__for_index()
        if dc is None:
            return None

        dimens, kw = dc[0], dc[1]

        index = np.arange(len(kw.Data))
        k_index = index // (dimens.NX * dimens.NY) + 1
        layer_index = (k_index - 1) * dimens.NX * dimens.NY
        i_index = layer_index % dimens.NX
        return CubeProperty(i_index, section=self)

    def get_i_j_k_index(
        self,
    ) -> Optional[Tuple[CubeProperty, CubeProperty, CubeProperty]]:
        dc = self.__for_index()
        if dc is None:
            return None

        dimens, kw = dc[0], dc[1]

        index = np.arange(len(kw.Data))
        k_index = index // (dimens.NX * dimens.NY) + 1
        layer_index = (k_index - 1) * dimens.NX * dimens.NY
        j_index = layer_index // dimens.NX
        i_index = layer_index % dimens.NX

        i = CubeProperty(i_index, section=self)
        j = CubeProperty(j_index, section=self)
        k = CubeProperty(k_index, section=self)
        return i, j, k


class UnInitializedGRID(UnInitializedSection):
    @staticmethod
    def get_famous_keyword() -> Dict[str, Type[Keyword]]:
        return GRID.get_famous_keyword()
