from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Base import DataFile, Type, Dict, Tuple, Union

import numpy as np

from ..Base import Section, Keyword, BaseKeywordCreator, UnknownKeyword
from ..ASCIIFile import ASCIIText


class CubeProperty(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data

    def __add__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data + other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data + other.Data)
        else:
            raise TypeError

    def __sub__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data - other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data - other.Data)
        else:
            raise TypeError

    def __mul__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data * other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data * other.Data)
        else:
            raise TypeError

    def __floordiv__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data // other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data // other.Data)
        else:
            raise TypeError

    def __div__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data / other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data / other.Data)
        else:
            raise TypeError

    def __truediv__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data / other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data / other.Data)
        else:
            raise TypeError

    def __mod__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
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
            return CubeProperty(self.Data // other), CubeProperty(self.Data % other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data // other.Data), CubeProperty(
                self.Data % other.Data
            )
        else:
            raise TypeError

    def __pow__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
    ) -> CubeProperty:
        if isinstance(other, (int, float, np.ndarray)):
            return CubeProperty(self.Data ** other)
        elif isinstance(other, CubeProperty):
            return CubeProperty(self.Data ** other.Data)
        else:
            raise TypeError

    def __radd__(
        self, other: Union[int, float, np.ndarray, CubeProperty]
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
            return CubeProperty(other // self.Data), CubeProperty(other % self.Data)
        elif isinstance(other, CubeProperty):
            return CubeProperty(other.Data // self.Data), CubeProperty(
                other.Data % self.Data
            )
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
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class FILHEAD(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class GRIDHEAD(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class GRIDUNIT(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class MAPAXES(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class MAPUNIT(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class ZCORN(Keyword):
    def __init__(self, data: np.ndarray) -> None:
        self.Data = data


class Mesh:
    def __init__(self) -> None:
        pass


class Cubs:
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__

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
    def __init__(self) -> None:
        pass


class Other:
    def __init__(self) -> None:
        pass


class SettingConstructor(BaseKeywordCreator):
    def init(self, data: str) -> INIT:
        return INIT()

    def create(self, data: str) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in GRID.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        adata = adata.replace_multiplication()
        fun = self.choose_fun(str(kw))
        return fun(adata)


class CubsConstructor(BaseKeywordCreator):
    def create_arrcube(self, data: str) -> ARRCube:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword(True))
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        return ARRCube(cubs, kw)

    def create(self, data: str) -> CubeProperty:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword(True))
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        famous_keyword = Cubs.get_famous_keyword()
        keyword_class: Type[CubeProperty] = famous_keyword[kw]
        return keyword_class(cubs)


class MeshConstructor(BaseKeywordCreator):
    def create(self, data: str) -> CubeProperty:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)
        adata = adata.replace_multiplication()
        adata = adata.to_slash()
        cubs = np.array(adata.split(), dtype=float)
        famous_keyword = GRID.get_famous_keyword()
        keyword_class: Type[CubeProperty] = famous_keyword[kw]
        return keyword_class(cubs)


class GRIDConstructor(BaseKeywordCreator):
    def create(self, data: str) -> Keyword:
        adata = ASCIIText(data)

        kw = str(adata.get_keyword())

        if str(kw) in GRID.get_mesh_keyword():
            return MeshConstructor().create(str(adata))
        elif str(kw) in GRID.get_cubs_keyword():
            return CubsConstructor().create(str(adata))
        elif "ARR" == str(kw)[:3]:
            return CubsConstructor().create_arrcube(str(adata))
        elif str(kw) not in GRID.get_famous_keyword().keys():
            kw = adata.get_keyword(True)
            return UnknownKeyword(str(kw), str(adata))
        else:
            return SettingConstructor().create(str(adata))


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
        self.Grid = Mesh()
        self.Cubs = Cubs()
        self.Setting = Setting()
        self.Other = Other()

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
    def get_constructor(cls) -> Type[BaseKeywordCreator]:
        return GRIDConstructor

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
