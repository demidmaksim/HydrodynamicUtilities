from HydrodynamicUtilities.Reader.ASCIIDataFileReader.Reader import (
    read,
    convert_to_data_file,
)
from pathlib import Path

folder = Path(r"C:\Users\demid\Desktop\GDM\tNav_Models")
files = read(folder / "DYNAMICMODEL.DATA")
data_file = convert_to_data_file(files)
pass
