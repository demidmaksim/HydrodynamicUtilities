from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Tuple

from pathlib import Path
from HydrodynamicUtilities.Models.Well import Trajectory
from HydrodynamicUtilities.Models.Strategy import ScheduleDataframe, ScheduleSheet
import numpy as np


def get_wname(string_data: str) -> str:
    return string_data.strip()


def get_xyzmd(
    data: Iterable[str],
    x_ind: int = 1,
    y_ind: int = 2,
    z_ind: int = 0,
    # md_ind: int = 3,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    # np.ndarray,
]:
    x = []
    y = []
    z = []
    # md = []
    for line in data:
        line_data = line.split()
        x.append(line_data[x_ind])
        y.append(line_data[y_ind])
        z.append(line_data[z_ind])
        # md.append(line_data[md_ind])

    return np.array(x), np.array(y), np.array(z)  # ,  np.array(md)


def convert_to_well(string_data: str) -> Trajectory:
    # trj = Trajectory()
    string_data = string_data.replace(",", ".")
    data = string_data.split("\n")
    wname = get_wname(data.pop(0))
    x, y, z = get_xyzmd(data)
    return


def read_file(file: Path):
    with open(file, "r") as file:
        string_data = file.read()

    data = string_data.split("\n\n")
