from HydrodynamicModelAnalysis.Models.DataFile import (
    ASCIIFilesIndexer,
    DataFile,
    Section,
)
from pathlib import Path
import time


def read(path: Path, parent: ASCIIFilesIndexer = None) -> ASCIIFilesIndexer:
    t = time.time()
    file = ASCIIFilesIndexer(path, parent)
    print(f"{path}: {round(time.time() - t, 2)}")
    for path in file.get_path():
        new_file = read(path, file)
        file.Entities.append(new_file)
    return file


def convert_to_data_file(
    files: ASCIIFilesIndexer,
    data_file: DataFile = None,
    active_sections: str = None,
) -> DataFile:
    if data_file is None:
        data_file = DataFile()

    if active_sections is None:
        act_sec: Section = getattr(data_file, "NoneSection")
    else:
        act_sec = getattr(data_file, active_sections)

    idf = files.Indexes.get_dataframe()

    if idf is None:
        return data_file

    for rid, row in idf.iterrows():
        kw = row["keyword"]

        if kw in ("INCLUDE",):
            kw_ind = int(row["include"]) - 1
            include_file = files.Entities[kw_ind]
            sec_name = act_sec.__class__.__name__
            data_file = convert_to_data_file(include_file, data_file, sec_name)

        elif kw in DataFile.get_section_name():
            act_sec = getattr(data_file, kw)

        else:
            start = int(row["start"])
            finish = int(row["finish"])
            data = files.get_text()[start:finish]
            creator = act_sec.get_constructor()
            kw_data = creator().create(data)
            setattr(act_sec, kw, kw_data)

    return data_file
