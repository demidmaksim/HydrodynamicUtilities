from __future__ import annotations

from HydrodynamicUtilities.Reader import EclipseBinaryParser as ebp
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

from HydrodynamicUtilities.Reader.ASCIIDataFileReader import Reader as adf


if __name__ == "__main__":
    # folder = Path(r"O:\Fil\Apt\GEO_2022_04_11\History\InWork\2022_10_24\RESULTS\History_to_2022_08_01_RPP12")
    # INIT = ebp.read(folder / "result.INSPEC")
    # UNRST = ebp.read(folder / "History_to_2022_08_01_RPP12.UNRST")
    folder = Path(r"O:\Fil\Apt\GEO_2022_04_11\History\Reference\2022_10_24\INCLUDE")
    # PORO = adf.convert_to_data_file(adf.read(folder / "PORO.GRDECL"), active_sections="GRID").GRID.Cubs.PORO.Data
    # CLAY = adf.convert_to_data_file(adf.read(folder / "CLAY.GRDECL"), active_sections="GRID").GRID.Cubs.ARRCLAY.Data
    DataFile = adf.convert_to_data_file(
        adf.read(folder / "ACTNUM.GRDECL"), active_sections="GRID"
    )
    DataFile.RUNSPEC.set_collected_keyword(name="DIMENS", nx=390, ny=64, nz=139)
    print(DataFile.RUNSPEC.DIMENS.get_statistic())

    pass
