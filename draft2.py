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
from PetrophysicalModel import Model

from HydrodynamicUtilities.Reader.ASCIIDataFileReader.Reader import (
    read,
    convert_to_data_file,
)


if __name__ == "__main__":
    folder = Path(r"O:\Fil\Apt\GEO_2022_04_11\History\Reference\2022_10_24\INCLUDE")
    model_clay = convert_to_data_file(
        read(folder / "CLAY.GRDECL"), active_sections="GRID"
    ).GRID.Cubs.ARRCLAY.Data
    model_poro = convert_to_data_file(
        read(folder / "PORO.GRDECL"), active_sections="GRID"
    ).GRID.Cubs.PORO.Data

    data = Model(
        {
            "PORO": model_poro,
            "CLAY": model_clay,
        },
        (
            "ARRDK = 0.5 + 2 * CLAY",
            "ARRPERM = 555 * PORO ** 2 * (1 - CLAY) ** 4.3",
            "PERMX = ARRPERM * exp(0.5 * ARRDK ** 2)",
            "PERMZ = ARRPERM * exp(- 0.5 * ARRDK ** 2)",
            "SWCR = 1 / (12.3 * PORO * (1 - clay) ** 2.7 + 1)",
            "ARRRF = 0.0311 * ln(PERMX) + 0.4443",
            "SGCR = (1 - SWCR) * (1 - ARRRF)",
            "SOWCR = (1 - SWCR) * (1 - ARRRF)",
            "SOGCR = SOWCR + (1 - SWCR - SOWCR) * 0.05",
            "KRW = ln(PERMX) * 0.0507 + 0.2562",
        ),
    )
    data.all_calc()
    pass
