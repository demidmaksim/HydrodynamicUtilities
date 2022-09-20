from __future__ import annotations


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


from pathlib import Path
from multiprocessing import Pool

from HydrodynamicModelAnalysis.Models.EclipseBinaryFile import SUMMARYList
from ..SecondaryFunctions import research_folder
from .BinaryFile import read


def research_read(
    folder: Path,
    multiprocessing: bool = False,
    log: bool = False,
) -> SUMMARYList:
    if multiprocessing:
        return __research_read_multiprocessing(folder, log)
    else:
        return __research_read_no_multiprocessing(folder, log)


def __research_read_multiprocessing(folder: Path, log: bool) -> SUMMARYList:
    list_of_path = research_folder(folder, ".SMSPEC", log=log)
    results = SUMMARYList()

    # if log:
    #     list_of_path = list(zip(list_of_path, [log] * len(list_of_path)))

    with Pool(len(list_of_path)) as p:
        answer = list(p.map(read, list_of_path))
        results.extend(answer)

    return results


def __research_read_no_multiprocessing(folder: Path, log: bool) -> SUMMARYList:
    list_of_path = research_folder(folder, ".SMSPEC", log=log)
    results = SUMMARYList()

    for path in list_of_path:
        results.append(read(path, log))

    return results
