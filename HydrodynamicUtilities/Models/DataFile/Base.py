from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Type, Any, List, Dict
    from HydrodynamicUtilities.Models.DataFile import DataFile

import abc

from ..Source.EtNKW_crutch import data as all_keyword
from .ASCIIFile import ASCIIText
from copy import deepcopy


class Section:
    __Keyword = dict()
    __AllKeyword = all_keyword

    def __init__(self, data_file: DataFile) -> None:
        self.__DataFile = data_file

    def __repr__(self) -> str:
        return self.__class__.__name__

    def get_data_file(self) -> DataFile:
        return self.__DataFile

    def __setattr__(self, key, value) -> None:
        if isinstance(value, str):
            super().__setattr__(key, ASCIIText(value))
        else:
            super().__setattr__(key, value)

    @abc.abstractmethod
    def get_start_date(self) -> Type[BaseKeywordCreator]:
        return BaseKeywordCreator

    @classmethod
    def get_constructor(cls) -> Type[BaseKeywordCreator]:
        return BaseKeywordCreator


class BaseKeywordCreator:
    @staticmethod
    def create_arithmetic(data: str) -> ARITHMETIC:
        results = []
        for row in data.split("\n"):
            if "/" not in row:
                row = str(ASCIIText(row))
                results.append(ArithmeticExpression(row))
        return ARITHMETIC(results)

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)
        kw = adata.get_keyword(True)
        if str(kw) == ARITHMETIC.__name__:
            return self.create_arithmetic(str(adata))
        else:
            return UnknownKeyword(str(kw), str(adata))

    def choose_fun(self, kw: str) -> Callable:
        return self.__getattribute__(kw.lower())


class Keyword:
    def __repr__(self) -> str:
        return self.__class__.__name__


class UnknownKeyword(Keyword):
    def __init__(self, name: str, data: str) -> None:
        self.Data = data
        self.Name = name

    def __repr__(self) -> str:
        return self.Name


class RowEntry:
    __Order: Dict[str, Any] = {}

    @classmethod
    @abc.abstractmethod
    def get_base_value(cls) -> Dict[str, Any]:
        pass


class OneRowKeyword(Keyword):
    pass


class ArithmeticExpression(Keyword):
    def __init__(self, string: str) -> None:
        self.Value = string
        self.Order = None

    def __repr__(self) -> str:
        return self.Value


class ARITHMETIC(Keyword):
    def __init__(self, calc: List[ArithmeticExpression]):
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
