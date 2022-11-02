from __future__ import annotations

from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

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
