from __future__ import annotations

from HydrodynamicUtilities.Reader.EclipseBinaryParser import read, read_binary
import plotly.express as px
from pathlib import Path
import pandas as pd
import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Dict

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd


from HydrodynamicUtilities.Reader.ASCIIDataFileReader.Reader import read, convert_to_data_file

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
    folder = Path(r"O:\Fil\Apt\GEO_2022_04_11\History\InWork\2022_10_24\RESULTS\History_to_2022_08_01_RPP12")
    # INIT = read(folder / "result.INSPEC")
    # UNRST = read(folder / "History_to_2022_08_01_RPP12.UNRST")

    PORO, clay, soil, swat, sgas = np.meshgrid(
        np.arange(0.05, 0.32, 0.01),
        np.arange(0, 1, 0.02),
        np.arange(0, 1, 0.1),
        np.arange(0, 1, 0.1),
        np.arange(0, 1, 0.1),
    )

    PORO = np.resize(PORO, (27 * 50 * 10 * 10 * 10))
    clay = np.resize(clay, (27 * 50 * 10 * 10 * 10))
    soil = np.resize(soil, (27 * 50 * 10 * 10 * 10))
    swat = np.resize(swat, (27 * 50 * 10 * 10 * 10))
    sgas = np.resize(sgas, (27 * 50 * 10 * 10 * 10))

    ARRDK = 0.5 + 2 * clay
    ARRPERM = 555 * PORO ** 2 * (1 - clay) ** 4.3
    PERMX = ARRPERM * np.exp(0.5 * ARRDK ** 2)
    PERMZ = ARRPERM * np.exp(- 0.5 * ARRDK ** 2)
    SWCR = 1 / (12.3 * PORO * (1 - clay) ** 2.7 + 1)
    ARRRF = 0.0311 * np.log(PERMX) + 0.4443
    SGCR = (1 - SWCR) * (1 - ARRRF)
    SOWCR = (1 - SWCR) * (1 - ARRRF)
    SOGCR = SOWCR + (1 - SWCR - SOWCR) * 0.05
    KRW = np.log(PERMX) * 0.0507 + 0.2562

    ow = LETWOModel(nw=1.5, ew=30, tw=0.75, now=2.7, eow=1.5, tow=2.3)
    og = LETGOModel(ng=1.2, eg=4, tg=3, nog=2.2, eog=1, tog=2)

    # SWAT = UNRST.SWAT[0]
    # SOIL = UNRST.SOIL[0]
    # SGAS = UNRST.SGAS[0]
    # SOWCR = INIT.SOWCR
    # SOGCR = INIT.SOGCR
    KRO_init = Baker2(ow, og).get_oil_rpp(SWCR, 0, SOWCR, SOGCR)

    KO_init = KRO_init * PERMX

    value = "PERMX"

    df = pd.DataFrame()
    df["PORO"] = PORO
    df["clay"] = clay
    df[value] = PERMX

    # results2 = Baker2(ow, og).get_oil_rpp(Swat2, Sgas2, SOWCR, SOGCR)
    fodler = Path(r"C:\Users\demid\Desktop")

    # model_clay = convert_to_data_file(read(fodler / "CLAY.GRDECL"), active_sections = "GRID").GRID.Cubs.ARRCLAY.Data
    # model_poro = convert_to_data_file(read(fodler / "PORO.GRDECL"), active_sections = "GRID").GRID.Cubs.PORO.Data
    # pattrn = (model_clay != 0) & (model_poro != 0)
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.6, 0.4],
        row_heights=[0.4, 0.6],
        #specs=[[{"type": "scattergeo", "rowspan": 2}, {"type": "bar"}],
        #       [None, {"type": "surface"}]]
        )

    fig.add_trace(
        go.Contour(
            x=PORO,
            y=clay,
            z=PERMX,
            contours={
                "start": 0.1,
                "end": 40,
                "size": 5
            },
            xaxis="x",
            yaxis="y"
        ),
        row=2,
        col=1,
    )
    """
    fig.add_trace(
        go.Histogram(
            x=model_poro[pattrn],
            xaxis = "x1",
            yaxis = "y1"
        ),
        row=1,
        col=1,
    )
    
    fig.add_trace(
        go.Histogram(
            y=model_clay[pattrn],
            xaxis="x2",
            yaxis="y2"
        ),
        row=2,
        col=2,
    )

    fig.update_xaxes(title_text="Poro", row=2, col=1, matches='x1')
    fig.update_yaxes(title_text="Clay", row=2, col=1, matches='y2')

    # fig.update_xaxes(row=1, col=1, matches='x1')
    fig.update_yaxes(matches='y2', row=2, col=2, )
    """

    fig.show()
    pass