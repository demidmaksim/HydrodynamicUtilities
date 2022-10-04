from HydrodynamicUtilities.Reader.ASCIIDataFileReader.Reader import (
    read,
    convert_to_data_file,
)
from pathlib import Path
import time


folder = Path(
    r"O:\Fil\Apt\GEO_2022_04_11\Predict\Reference\BaseHistoryPrediction\2022_09_12"
)
files = read(folder / "History_to_2022_08_01_7days_all_WellTest.DATA")
t = time.time()
data_file = convert_to_data_file(files)
print(f"convert: {round(time.time() - t, 2)}")
pass
