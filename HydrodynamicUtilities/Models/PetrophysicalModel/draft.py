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

from HydrodynamicUtilities.Models.PetrophysicalModel.CoreDraft import (
    LETWOModel,
    LETGOModel,
    Baker2,
)


from HydrodynamicUtilities.Reader.ASCIIDataFileReader.Reader import (
    read,
    convert_to_data_file,
)


if __name__ == "__main__":
    folder = Path(
        r"O:\Fil\Apt\GEO_2022_04_11\History\InWork\2022_10_24\RESULTS\History_to_2022_08_01_RPP12"
    )
    # INIT = read(folder / "result.INSPEC")
    # UNRST = read(folder / "History_to_2022_08_01_RPP12.UNRST")

    PORO, clay = np.meshgrid(np.arange(0.05, 0.32, 0.01), np.arange(0, 1, 0.02))
    PORO = np.resize(PORO, (27 * 50,))
    clay = np.resize(clay, (27 * 50,))
    ARRDK = 0.5 + 2 * clay
    ARRPERM = 555 * PORO**2 * (1 - clay) ** 4.3
    PERMX = ARRPERM * np.exp(0.5 * ARRDK**2)
    PERMZ = ARRPERM * np.exp(-0.5 * ARRDK**2)
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
    fodler = Path(r"O:\Fil\Apt\GEO_2022_04_11\History\Reference\2022_10_24\INCLUDE")

    model_clay = convert_to_data_file(
        read(fodler / "CLAY.GRDECL"), active_sections="GRID"
    ).GRID.Cubs.ARRCLAY.Data
    model_poro = convert_to_data_file(
        read(fodler / "PORO.GRDECL"), active_sections="GRID"
    ).GRID.Cubs.PORO.Data
    pattrn = (model_clay != 0) & (model_poro != 0)
    fig = make_subplots(
        rows=2,
        cols=2,
        column_widths=[0.6, 0.4],
        row_heights=[0.4, 0.6],
        # specs=[[{"type": "scattergeo", "rowspan": 2}, {"type": "bar"}],
        #       [None, {"type": "surface"}]]
    )

    fig.add_trace(
        go.Contour(
            x=PORO,
            y=clay,
            z=PERMX,
            contours={
                "start": 1,
                "end": 40,
                "size": 5,
                # "type": "log",
                "coloring": "lines",
                #'size': [0.28, 0.22, 0.15, 0.1, 0.07, 0.06, 0.05, 0.04, 0.03],
                "showlabels": True,
            },
            xaxis="x",
            yaxis="y",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=model_poro[np.arange(0, len(model_poro), 1000)],
            y=model_clay[np.arange(0, len(model_poro), 1000)],
            mode="markers",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Histogram(x=model_poro[pattrn], xaxis="x1", yaxis="y1"),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Histogram(y=model_clay[pattrn], xaxis="x2", yaxis="y2"),
        row=2,
        col=2,
    )

    fig.update_xaxes(title_text="Poro", row=2, col=1, matches="x1")
    fig.update_yaxes(title_text="Clay", row=2, col=1, matches="y2")

    # fig.update_xaxes(row=1, col=1, matches='x1')
    fig.update_yaxes(
        matches="y2",
        row=2,
        col=2,
    )

    fig.show()
    pass
