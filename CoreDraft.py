from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Dict

import numpy as np


class LETGOModel:
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
        self.SGL = sgl  # 1
        self.SGU = sgu  # 2
        self.SGCR = sgcr  # 3
        self.SOGCR = sogcr  # 4
        self.KROLG = krolg  # 5
        self.KRORG = krorg  # 6
        self.KRGR = krgr  # 7
        self.KRGU = krgu  # 8
        self.PCOG = pcog  # 9
        self.NOG = nog  # 10
        self.NG = ng  # 11
        self.NPG = npg  # 12
        self.SPCG = spcg  # 13
        self.TG = tg  # 14
        self.EG = eg  # 15
        self.TOG = tog  # 16
        self.EOG = eog  # 17

    def gas_nrpp(
        self,
        sngas: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        l = self.NG
        e = self.EG
        t = self.TG
        krg = self.KRGR
        return krg * sngas ** l / (sngas ** l + e * (1 - sngas) ** t)

    def oil_nrpp(
        self,
        sngas: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        l = self.NOG
        e = self.EOG
        t = self.TOG
        kro = self.KRORG
        return kro * (1 - sngas) ** l / ((1 - sngas) ** l + e * sngas ** t)


class LETWOModel:
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
        swl: float = 0,
        swu: float = 1,
        swcr: float = 0,
        sowcr: float = 0,
        krolw: float = 1,
        krorw: float = 1,
        krwr: float = None,
        krwu: float = None,
        pcow: float = 0,
        now: float = 4,
        nw: float = 4,
        npw: float = 4,
        spco: float = -1,
        tw: float = 2,
        ew: float = 1,
        tow: float = 2,
        eow: float = 1,
    ) -> None:
        self.SWL = swl  # 1
        self.SWU = swu  # 2
        self.SWCR = swcr  # 3
        self.SOWCR = sowcr  # 4
        self.KROLW = krolw  # 5
        self.KRORW = krorw  # 6
        self.KRWR = krwr  # 7
        self.KRWU = krwu  # 8
        self.PCOW = pcow  # 9
        self.NOW = now  # 10
        self.NW = nw  # 11
        self.NPW = npw  # 12
        self.SPCO = spco  # 13
        self.TW = tw  # 14
        self.EW = ew  # 15
        self.TOW = tow  # 16
        self.EOW = eow  # 17

    def wat_nrpp(
        self,
        snwat: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        l = self.NW
        e = self.EW
        t = self.TW
        krg = self.KRWR
        return krg * snwat ** l / (snwat ** l + e * (1 - snwat) ** t)

    def oil_nrpp(
        self,
        snwat: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        l = self.NOW
        e = self.EOW
        t = self.TOW
        kro = self.KRORW
        return kro * (1 - snwat) ** l / ((1 - snwat) ** l + e * snwat ** t)


class Normalizer:
    @staticmethod
    def get_oil_normalize(
        soil: Union[float, int, np.ndarray],
        sopcr: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        return (1 - soil) / (1 - sopcr)

    @staticmethod
    def get_wat_normalize(
        swat: Union[float, int, np.ndarray],
        swcr: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        return (swat - swcr) / (1 - swcr)

    @staticmethod
    def get_gas_normalize(
        sgas: Union[float, int, np.ndarray],
        sgcr: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        return (sgas - sgcr) / (1 - sgcr)


class Baker2:
    def __init__(self, ow: LETWOModel, og: LETGOModel) -> None:
        self.OW = ow
        self.OG = og
        self.Normalizer = Normalizer()

    def get_oil_rpp(
        self,
        swat: Union[float, int, np.ndarray],
        sgas: Union[float, int, np.ndarray],
        sowcr: Union[float, int, np.ndarray],
        sogcr: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        fun = self.Normalizer.get_oil_normalize
        soil = 1 - swat - sgas
        now = fun(soil, sowcr)
        nog = fun(soil, sogcr)
        krow = self.OW.oil_nrpp(now)
        krog = self.OG.oil_nrpp(nog)
        return (sgas * krog + swat * krow) / (sgas + swat)

    def get_wat_rpp(
        self,
        swat: Union[float, int, np.ndarray],
        swcr: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        fun = self.Normalizer.get_wat_normalize
        nw = fun(swat, swcr)
        return self.OW.wat_nrpp(nw)

    def get_gas_rpp(
        self,
        sgas: Union[float, int, np.ndarray],
        sgcr: Union[float, int, np.ndarray],
    ) -> Union[float, int, np.ndarray]:
        fun = self.Normalizer.get_wat_normalize
        nw = fun(sgas, sgcr)
        return self.OG.gas_nrpp(nw)


class RegionsRPP:
    def __init__(self, data: Dict[int: Baker2]) -> None:
        self.Data = data



if __name__ == "__main__":

    SWCR = 0.37228362
    SGCR = 0.00
    SOGCR = 0.309324395
    SOWCR = 0.292566923

    Soil1 = 0.372123639
    Swat1 = 0.373014822
    Sgas1 = 0.254861539

    Soil2 = 0.62759334
    Swat2 = 0.37240666
    Sgas2 = 0

    ow = LETWOModel(nw=1.5, ew=30, tw=0.75, now=2.7, eow=1.5, tow=2.3)
    og = LETGOModel(ng=1.2, eg=4, tg=3, nog=2.2, eog=1, tog=2)

    results1 = Baker2(ow, og).get_oil_rpp(Swat1, Sgas1, SOWCR, SOGCR)
    results2 = Baker2(ow, og).get_oil_rpp(Swat2, Sgas2, SOWCR, SOGCR)
    print(results1)
    print(results2)
