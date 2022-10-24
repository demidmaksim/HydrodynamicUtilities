from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .Samples import BaseSamples,  CompositeSample

import pandas
import numpy

from abc import abstractmethod


class BaseRPP:
    pass


class SimpleRPP:

    __phase_white_list = ("wat", "oil", "gas")

    def __init__(
            self,
            saturation: np.ndarray,
            phase_permeability: np.ndarray,
            phase: str,
            sample: BaseSamples,
            normalized: bool = False,
    ) -> None:
        self.Saturation = saturation
        self.PhasePermeability = phase_permeability
        if phase in self.__phase_white_list:
            self.Phase = phase
        else:
            raise KeyError
        self.Sample = sample
        self.Normalized = normalized

    def __repr__(self) -> str:
        return self.Phase


class TwoPhaseRPP:
    def __init__(
            self,
            first: SimpleRPP,
            second: SimpleRPP,
    ) -> None:
        self.First = first
        self.Second = second

    def __repr__(self) -> str:
        return f"{self.First.Phase}/{self.Second.Phase}"
