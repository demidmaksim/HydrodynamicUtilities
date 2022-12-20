from HydrodynamicUtilities.Models.DataFile.Base import (
    Section,
    UnInitializedSection,
)
from HydrodynamicUtilities.Models.DataFile.DataFile import (
    DataFile,
    UnInitializedDataFile,
)
from HydrodynamicUtilities.Models.DataFile.IndexedFile import ASCIIFilesIndexer

from pathlib import Path
import time
from HydrodynamicUtilities.Models.DataFile.SectionConstructors import get_constructor


def read(
        path: Path,
        parent: ASCIIFilesIndexer = None
) -> ASCIIFilesIndexer:
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
            string_data = files.get_text()[start:finish]
            creator = get_constructor(act_sec)
            kw_data = creator.create(string_data, data_file)
            setattr(act_sec, kw, kw_data)

    return data_file


def convert_to_un_initialized_data_file(
    files: ASCIIFilesIndexer,
    data_file: DataFile = None,
    active_sections: str = None,
) -> UnInitializedDataFile:
    t = time.time()
    if data_file is None:
        data_file = UnInitializedDataFile()

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
            sec_name = act_sec.__repr__()
            data_file = convert_to_un_initialized_data_file(
                include_file, data_file, sec_name
            )

        elif kw in DataFile.get_section_name():
            act_sec = getattr(data_file, kw)

        else:
            start = int(row["start"])
            finish = int(row["finish"])
            string_data = files.get_text()[start:finish]
            creator = get_constructor(act_sec)
            kw_data = creator.create(string_data, data_file)
            setattr(act_sec, kw, kw_data)
    print(f"{files.Path}: {round(time.time() - t, 2)}")

    return data_file


def convert_to_schedule_dataframe(
    files: ASCIIFilesIndexer,
    data_file: DataFile = None,
) -> DataFile:
    if data_file is None:
        data_file = DataFile()

    act_sec = data_file.SCHEDULE
    famous_kw = act_sec.get_famous_keywords()
    idf = files.Indexes.get_dataframe()

    if idf is None:
        return data_file

    for rid, row in idf.iterrows():
        kw = row["keyword"]
        if kw in famous_kw or kw == "DATES":
            start = int(row["start"])
            finish = int(row["finish"])
            string_data = files.get_text()[start:finish]
            creator = act_sec.get_constructor()
            kw_data = creator().create(string_data, data_file)
            setattr(act_sec, kw, kw_data)

        elif kw in ("INCLUDE",):
            kw_ind = int(row["include"]) - 1
            include_file = files.Entities[kw_ind]
            data_file = convert_to_schedule_dataframe(include_file, data_file)
    return data_file


def initialization_data_file(
        data_file: UnInitializedDataFile,
) -> DataFile:
    results = DataFile()
    for sec in data_file.get_section_name():
        act_un_init_sec: UnInitializedSection = getattr(data_file, sec)
        act_sec: Section = getattr(results, sec)
        if act_un_init_sec.__repr__() != "SCHEDULE":
            for kw in act_un_init_sec.Order:
                act_sec.set_keyword(kw)

    results.SCHEDULE = data_file.SCHEDULE

    return results
