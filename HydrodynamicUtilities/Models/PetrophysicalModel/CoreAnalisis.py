from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union

import numpy as np
from numbers import Number


class LET:
    def __init__(
            self,
            l: Union[float, int],
            e: Union[float, int],
            t: Union[float, int],
            max_x: Union[float, int] = 1,
            max_y: Union[float, int] = 1,
    ) -> None:
        self.L = l
        self.E = e
        self.t = t

    def get_value(
            self,
            x: np.ndarray,
    ) -> None:
        pass


class AbstractPhase:
    def __init__(
            self,
            permeability: np.ndarray,
            saturation: np.ndarray,
            pgcr: Union[float, int],
            max_phase_perm: Union[float, int],
            absolute_permeability: Union[float, int] = None,
    ) -> None:
        self.Perm = permeability
        self.Sat = saturation
        self.PGCR = pgcr
        self.MaxPhasePerm = max_phase_perm
        if absolute_permeability is None:
            self.AbsPerm = max_phase_perm
        else:
            self.AbsPerm = absolute_permeability

    def get_normalized_saturation(self) -> np.ndarray:
        return (1 - self.Sat) / (1 - self.PGCR)

    def get_normalized_perm(self) -> np.ndarray:
        return self.Perm / self.MaxPhasePerm


class OilPhase(AbstractPhase):
    pass


class WatPhase(AbstractPhase):
    pass


class GasPhase(AbstractPhase):
    pass



class CoreSample:
    def __init__(
            self,
            wp: WatPhase,
            op: OilPhase,
            gp: OilPhase,
    ) -> None:
        self.WP = wp
        self.OP = op
        self.GP = gp