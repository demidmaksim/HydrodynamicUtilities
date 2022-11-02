from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from typing import Union, List, Optional

import pandas
import numpy

from abc import abstractmethod


class BaseSamples:
    def __init__(
        self,
        name: str,
        perm: Union[float, int],
        poro: Union[float, int],
    ) -> None:
        self.Name = name
        self.Perm = perm
        self.Poro = poro

    def __repr__(self) -> str:
        return self.Name


class SingleSample(BaseSamples):
    def __init__(
        self, name: str, perm: Union[float, int], poro: Union[float, int]
    ) -> None:
        super().__init__(name, perm, poro)


class CompositeSample(BaseSamples):
    def __init__(
        self,
        name: str,
        perm: Union[float, int],
        poro: Union[float, int],
        elements: Optional[List[SingleSample]] = None,
    ) -> None:
        super().__init__(name, perm, poro)

        self.Elements = elements
