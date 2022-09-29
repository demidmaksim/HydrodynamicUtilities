from HydrodynamicUtilities.Reader.ASCIIDataFileReader.Reader import (
    read,
    convert_to_data_file,
)
from pathlib import Path

folder = Path(r"O:\Fil\Apt\GEO_2022_04_11\History\Reference\2022_08_01")
files = read(folder / "History_to_2022_08_01_1days_all_WellTest.DATA")
data_file = convert_to_data_file(files)
pass
