from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Any, List, Dict
    from HydrodynamicUtilities.Models.DataFile import DataFile

import abc

from ..Source.EtNKW_crutch import data as all_keyword
from .ASCIIFile import ASCIIText
from copy import deepcopy


class Section:
    __Keyword: Type[Keyword] = dict()
    __AllKeyword = all_keyword

    def __init__(self, data_file: DataFile) -> None:
        self.__DataFile = data_file

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __setattr__(self, key, value) -> None:
        if isinstance(value, str):
            super().__setattr__(key, ASCIIText(value))
        elif isinstance(value, Keyword):
            value.ParentSection = self
            super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)

    def set_keyword(self, data: Keyword) -> None:
        if isinstance(data, ARITHMETIC):
            pass
        elif isinstance(data, Keyword):
            self.__setattr__(data.__repr__(), data)
        else:
            pass

    def get_data_file(self) -> DataFile:
        return self.__DataFile

    @abc.abstractmethod
    def get_famous_keyword(self) -> Dict[str, Type[Keyword]]:
        pass

    def set_collected_keyword(self, name: str, **kwargs: Dict[str, Any]) -> None:
        value = self.get_famous_keyword()[name]
        kw = value(**kwargs)
        self.__setattr__(name, kw)


class UnInitializedSection(Section):
    def __init__(self, data_file: DataFile) -> None:
        super().__init__(data_file)
        self.Order = []

    def __setattr__(self, key: str, value: Any) -> None:
        if key not in self.__dict__.keys() and isinstance(value, Keyword):
            super().__setattr__(key, [value])
            self.Order.append(value)
        elif not isinstance(value, Keyword):
            super().__setattr__(key, value)
        else:
            value_list = self.__getattribute__(key)
            value_list.append(value)
            self.Order.append(value)

    def __repr__(self) -> str:
        data = self.__class__.__name__
        return data.split("UnInitialized")[1]

    @abc.abstractmethod
    def get_famous_keyword(self) -> Dict[str, Type[Keyword]]:
        pass


class Keyword:
    def __init__(self, section: Section = None, **kwargs) -> None:
        self.ParentSection = section

    def __repr__(self) -> str:
        return self.__class__.__name__


class UnknownKeyword(Keyword):
    def __init__(self, name: str, data: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Data = data
        self.Name = name

    def __repr__(self) -> str:
        return self.Name


class ArithmeticExpression(Keyword):
    def __init__(self, string: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.Value = string
        self.Order = None

    def __repr__(self) -> str:
        return self.Value


class ARITHMETIC(Keyword):
    def __init__(self, calc: List[ArithmeticExpression], **kwargs):
        super().__init__(**kwargs)
        self.__Calculations = calc

    @property
    def expressions(self) -> List[ArithmeticExpression]:
        return self.__Calculations

    def __add__(self, other: ARITHMETIC) -> ARITHMETIC:
        new = deepcopy(self)
        for oe in other.expressions:
            new.append(oe)
        return new

    def append(self, other: ArithmeticExpression) -> None:
        other.Order = len(self.__Calculations)
        self.__Calculations.append(other)
