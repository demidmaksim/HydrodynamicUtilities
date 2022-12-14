from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Union
    from HydrodynamicUtilities.Models.EclipseBinaryFile import (
        SUMMARY,
        EclipseBinaryData,
    )
    from .BaseBinaryReader import RowBinaryData


import os
import numpy as np
import datetime as dt
import time

from pathlib import Path

from .BaseBinaryReader import BinaryReader
from HydrodynamicUtilities.Models.EclipseBinaryFile import (
    SUMMARYHeader,
    BinaryData,
    SUMMARY,
    INIT,
    UNRSTRSSPEC,
)
from HydrodynamicUtilities.Models.Time import TimeVector as Time


class Convertor:
    @classmethod
    def to_as_it_is(cls, data: RowBinaryData) -> Dict[str, Any]:
        newdata = dict()
        for content in data:
            keyword = content.keyword
            values = content.decode()
            newdata[keyword] = values
        return newdata

    @staticmethod
    def get_datetime(start_date: np.ndarray) -> dt.datetime:
        day = start_date[0]
        month = start_date[1]
        year = start_date[2]
        hour = start_date[3]
        minute = start_date[4]
        second = int(start_date[5])
        return dt.datetime(year, month, day, hour, minute, second)

    @classmethod
    def get_datetime64(cls, start_date: np.ndarray) -> np.datetime64:
        datetime = cls.get_datetime(start_date)
        strftime = datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return np.datetime64(strftime)

    @classmethod
    def to_binary_data(cls, data: RowBinaryData) -> BinaryData:
        return BinaryData(Convertor.to_as_it_is(data))


def to_summary(calc_name: str, smspec: RowBinaryData, unsmry: RowBinaryData) -> SUMMARY:
    smspec_dict = Convertor.to_as_it_is(smspec)
    unsmry_dict = Convertor.to_as_it_is(unsmry)

    if "NAMES" in smspec_dict.keys():
        value = smspec_dict.pop("NAMES")
        smspec_dict["WGNAMES"] = value

    if "NAMES" in smspec_dict.keys():
        value = smspec_dict.pop("NAMES")
        smspec_dict["WGNAMES"] = value

    summary_header = SUMMARYHeader(
        np.array(smspec_dict["KEYWORDS"]),
        np.array(smspec_dict["WGNAMES"]),
        np.array(smspec_dict["NUMS"]),
        np.array(smspec_dict["UNITS"]),
    )

    summary = SUMMARY(
        calc_name,
        unsmry_dict["PARAMS"],
        get_time_vector(smspec_dict, unsmry_dict),
        summary_header,
    )

    return summary


def to_init(row_data: RowBinaryData, row_inspec: RowBinaryData) -> INIT:
    data = Convertor.to_as_it_is(row_data)
    inspec = Convertor.to_as_it_is(row_inspec)
    return INIT(BinaryData(data), BinaryData(inspec))


def to_unrst_rsspec(
    row_unrst: RowBinaryData,
    row_rsspec: RowBinaryData,
) -> UNRSTRSSPEC:
    unrst = Convertor.to_as_it_is(row_unrst)
    rsspec = Convertor.to_as_it_is(row_rsspec)
    return UNRSTRSSPEC(BinaryData(unrst), BinaryData(rsspec))


def get_time_vector(
    smspec: Dict[str, Any],
    unsmry: Dict[str, Any],
) -> Time:
    datetime = Convertor.get_datetime64(smspec["STARTDAT"])
    dey_vector: np.ndarray = unsmry["PARAMS"][:, 0]
    results = []
    for day_id, day in enumerate(dey_vector):
        day *= 3600 * 24 * 10**3
        results.append(datetime + np.timedelta64(int(day), "ms"))

    return Time(np.array(results))


def read(link: Path, log: bool = True) -> Union[EclipseBinaryData]:
    filename, file_extension = os.path.splitext(link.name)
    t = time.time()
    if file_extension in (".SMSPEC", ".UNSMRY"):
        results = read_summary(link)
    elif file_extension in (".INIT", ".INSPEC"):
        results = read_init(link)
    elif file_extension in (".UNRST", ".RSSPEC"):
        results = read_unrst_rsspec(link)
    else:
        results = read_binary(link)

    if log:
        print(f"File {link} read in {round(time.time() - t, 2)} seconds")

    return results


def read_summary(link: Path) -> SUMMARY:
    folder = link.parent
    filename, file_extension = os.path.splitext(link.name)

    if file_extension.upper() == ".SMSPEC":
        smspec = BinaryReader.read_all_file(folder / (filename + file_extension))
        unsmry = BinaryReader.read_all_file(folder / (filename + ".UNSMRY"))
    elif file_extension.upper() == ".UNSMRY":
        smspec = BinaryReader.read_all_file(folder / (filename + ".SMSPEC"))
        unsmry = BinaryReader.read_all_file(folder / (filename + file_extension))
    else:
        raise ValueError(f"File extension can only be '.UNSMRY', '.SMSPEC'")

    return to_summary(filename, smspec, unsmry)


def read_init(link: Path) -> INIT:
    folder = link.parent
    filename, file_extension = os.path.splitext(link.name)

    if file_extension.upper() == ".INIT":
        init = BinaryReader.read_all_file(folder / (filename + file_extension))
        inspec = BinaryReader.read_all_file(folder / (filename + ".INSPEC"))
    elif file_extension.upper() == ".INSPEC":
        init = BinaryReader.read_all_file(folder / (filename + ".INIT"))
        inspec = BinaryReader.read_all_file(folder / (filename + file_extension))
    else:
        raise ValueError(f"File extension can only be '.INIT', '.INSPEC'")

    return to_init(init, inspec)


def read_unrst_rsspec(link: Path) -> UNRSTRSSPEC:
    folder = link.parent
    filename, file_extension = os.path.splitext(link.name)

    if file_extension.upper() == ".UNRST":
        unrst = BinaryReader.read_all_file(folder / (filename + file_extension))
        rsspec = BinaryReader.read_all_file(folder / (filename + ".RSSPEC"))
    elif file_extension.upper() == ".RSSPEC":
        unrst = BinaryReader.read_all_file(folder / (filename + ".UNRST"))
        rsspec = BinaryReader.read_all_file(folder / (filename + file_extension))
    else:
        raise ValueError(f"File extension can only be '.UNRST', '.RSSPEC'")

    return to_unrst_rsspec(unrst, rsspec)


def read_binary(link: Path) -> BinaryData:
    rbd = BinaryReader().read_all_file(link)
    return Convertor.to_binary_data(rbd)
