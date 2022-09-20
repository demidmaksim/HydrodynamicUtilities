from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from pathlib import Path
import os


def research_folder(
    folder: Path,
    extension: str,
    results: list = None,
    deep: bool = True,
    log: bool = False,
) -> List[Path]:
    if results is None:
        results: List[Path] = list()

    for file in os.listdir(folder):
        if Path(folder / file).is_dir() and deep:
            research_folder(folder / file, extension, results, deep)
        else:
            filename, file_extension = os.path.splitext((folder / file))
            if file_extension == extension:
                if log:
                    print(folder / file)
                results.append(folder / file)

    return results
