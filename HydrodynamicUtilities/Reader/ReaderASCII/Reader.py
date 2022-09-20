from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Tuple, Optional
    from HydrodynamicModelAnalysis.Models.DataFile import Section

from .ASCIIFile import ASCIIFile, ASCIIRow, all_ecl_keyword
from HydrodynamicModelAnalysis.Models.DataFile import DataFile

from HydrodynamicModelAnalysis.Models import ScheduleRow, ScheduleSheet
from HydrodynamicModelAnalysis.Models import TimePoint, TimeVector
from HydrodynamicModelAnalysis.Models.Source.EclipseScheduleNames import (
    ScheduleKeyword,
    WELLTRACK,
)
from datetime import datetime
from HydrodynamicModelAnalysis.Reader.EclipseBinaryParser import read_binary
import os


def read_ascii_file(link: Path) -> ASCIIFile:
    with open(link, "r") as file:
        text = file.read()
    return ASCIIFile(text, link)


def check_custom_cube(ascii_row: ASCIIRow) -> bool:
    return ascii_row[:3].upper() == "ARR"


def check_special_word(string: ASCIIRow, words: Tuple[str, ...]) -> bool:
    if string.chek_skip():
        return False
    word = string.get_first_word()
    if word in words:
        return True
    else:
        return False


def read_ascii(path: Path, ascii_file: ASCIIFile) -> None:
    add_ascii = read_ascii_file(path)
    ascii_file.append(add_ascii)


def read_binary_data(
    path: Path,
    ascii_file: ASCIIFile,
    datafile: DataFile,
    section: Optional[Section],
) -> None:
    data = read_binary(path)
    for key, value in data.__dict__.items():
        kwp = datafile.NoneSection.get_keyword(key)
        kw = kwp(method="as_it_is", data=value, datafile=datafile)
        setattr(section, key, kw)
    pass


def read_path(
    ascii_file: ASCIIFile,
    datafile: DataFile,
    section: Optional[Section],
) -> None:
    ascii_path = ascii_file.read_path()
    path = ascii_path.get_path()
    target_file = ascii_file.Path.parent / path
    filename, file_extension = os.path.splitext(target_file)
    if file_extension not in (".EGRID",):
        read_ascii(target_file, ascii_file)
    elif file_extension in (".EGRID",):
        read_binary_data(target_file, ascii_file, datafile, section)
    else:
        raise ValueError


"""
def read_arithmetic(
    ascii_file: ASCIIFile,
    datafile: DataFile,
    section: Optional[Section],
) -> None:
    ascii_file.read_string()
    ar = ARITHMETIC(ascii_file.read_aritmetic())
    if hasattr(section, "ARITHMETIC"):
        ar_sec = getattr(section, "ARITHMETIC")
        ar_sec.append(ar)
    else:
        setattr(section, "ARITHMETIC", ar)


def read_keyword(
    ascii_file: ASCIIFile,
    datafile: DataFile,
    section: Optional[Section],
) -> None:
    if section is None:
        raise ValueError

    predict = ascii_file.read_string(predict=True)

    if check_special_word(predict, section.Keyword):
        line = ascii_file.read_string()
        keyword_name = line.get_first_word()
        keyword = section.Keyword[keyword_name]
        value = keyword(data=ascii_file, datafile=datafile)
        setattr(section, keyword.__name__, value)

    elif check_special_word(predict, section.AllKeyword):
        line = ascii_file.read_string()
        keyword_name = line.get_first_word()
        if type(section) == NoneSection:
            kw = section.get_keyword(keyword_name)
            value = kw(data=ascii_file, datafile=datafile)
        elif section.__class__.__name__ != "GRID":
            value = UnknownKeyWord(data=ascii_file, datafile=datafile)
        else:
            value = UnknownOneSlashWord(data=ascii_file, datafile=datafile)
        setattr(section, keyword_name.upper(), value)

    else:
        ascii_file.read_string()


def read_custom_cube(
    ascii_file: ASCIIFile,
    datafile: DataFile,
    section: Optional[Section],
) -> None:
    line = ascii_file.read_string()
    keyword_name = line.get_first_word()
    value = CubeProperty(data=ascii_file, datafile=datafile)
    setattr(section, keyword_name.upper(), value)
"""


def read_sch_keyword(
    ascii_file: ASCIIFile,
    data_file: DataFile,
    date: TimePoint,
) -> None:
    f_line = ascii_file.read_string()
    sheet_pattern = ScheduleKeyword.keyword[f_line.clean().Text]
    while ascii_file.not_end:
        line = ascii_file.read_to_slash()

        if line.clean() == "/":
            break

        line = line.clean_slash()

        line = line.replace_multiplication
        if date is not None:
            data = [date.to_datetime64()]
        else:
            data = [date]

        target_data = line.split_not_mask()

        if sheet_pattern.LastMulti:
            base_length = len(sheet_pattern.Order) - 1
            new_data = data[:]
            new_data.extend(target_data[:base_length])
            for i in range(len(target_data) - base_length):
                target_row = new_data[:]
                target_row.append(target_data[base_length + i])
                s_row = ScheduleRow(sheet_pattern, target_row)
                data_file.SCHEDULE.SDF.add_row(s_row)
        else:
            data.extend(target_data)
            s_row = ScheduleRow(sheet_pattern, data)
            data_file.SCHEDULE.SDF.add_row(s_row)


def read_welltrack(
    ascii_file: ASCIIFile,
    datafile: DataFile,
    date: TimePoint,
) -> None:
    line = ascii_file.read_string()
    full_well_name = line.split()[1]
    well_name_list = full_well_name.split(":")
    if len(well_name_list) != 1:
        bore = well_name_list[1]
    else:
        bore = 0

    data = ascii_file.read_to_slash().clean().split()
    x = data[0:-1:4]
    y = data[1:-1:4]
    z = data[2:-1:4]
    md = data[3:-1:4]
    sheet = ScheduleSheet(WELLTRACK)
    sheet.DF[WELLTRACK.X] = x
    sheet.DF[WELLTRACK.Y] = y
    sheet.DF[WELLTRACK.Z] = z
    sheet.DF[WELLTRACK.MD] = md
    sheet.DF[WELLTRACK.WellName] = well_name_list[0]
    sheet.DF[WELLTRACK.BoreName] = bore
    sheet.DF["Time"] = date.to_datetime64()
    sheet.DF[WELLTRACK.PointNumber] = sheet.DF.index
    datafile.SCHEDULE.SDF = datafile.SCHEDULE.SDF + sheet
    pass


def read_dates(ascii_file: ASCIIFile, datafile: DataFile) -> None:
    ascii_file.read_string()
    while ascii_file.not_end:
        predict = ascii_file.read_to_slash(predict=True)

        if check_special_word(predict, all_ecl_keyword):
            break

        line = ascii_file.read_to_slash()

        if line.clean() == "/":
            break

        line = line.clean_slash()
        data = line.split()
        if len(data) == 3:
            str_date = f"{data[0]} {data[1]} {data[2]}"
            date = datetime.strptime(str_date, "%d %b %Y")
        elif len(data) == 4:
            date = datetime.strptime(line.Text.upper(), "%d %b %Y %H:%M:%S")
        else:
            raise ValueError

        if datafile.SCHEDULE.Dates is not None:
            datafile.SCHEDULE.Dates.append(TimePoint(date))
        else:
            datafile.SCHEDULE.Dates = TimeVector([str(date)])


"""
def __read_schedule_section(ascii_file: ASCIIFile, datafile: DataFile):
    date = datafile.RUNSPEC.get_start_date()

    if datafile.SCHEDULE.Dates is not None:
        datafile.SCHEDULE.Dates.append(date)
    elif date is None:
        pass
    else:
        datafile.SCHEDULE.Dates = TimeVector([str(date)])

    while ascii_file.not_end:
        predict = ascii_file.read_string(predict=True)

        if predict.Text.strip() in datafile.Section:
            break
        elif predict.get_first_word() in ("INCLUDE", "GDFILE"):
            read_path(ascii_file, datafile, section=datafile.SCHEDULE)
        elif predict.get_first_word() == "ARITHMETIC":
            read_arithmetic(ascii_file, datafile, datafile.SCHEDULE)
        elif predict.get_first_word() == "WELLTRACK":
            read_welltrack(ascii_file, datafile, date)
        elif predict.get_first_word() == "DATES":
            read_dates(ascii_file, datafile)
            date = datafile.SCHEDULE.Dates[-1]
        elif predict.clean().Text in ScheduleKeyword.keyword.keys():
            read_sch_keyword(ascii_file, datafile, date)
        elif predict.clean().Text in all_ecl_keyword:
            line = ascii_file.read_string()
            keyword_name = line.get_first_word()
            dsd = DirtySchData(keyword_name, data=ascii_file)
            datafile.SCHEDULE.DirtyData.append(dsd)
        elif predict.chek_skip():
            ascii_file.read_string()
        else:
            ascii_file.read_string()


def read_schedule_section(link: Path) -> DataFile:
    ascii_file = read_ascii_file(link)
    datafile = DataFile()
    __read_schedule_section(ascii_file, datafile)
    return datafile


def read_data_file(link: Path):
    file = read_ascii_file(link)

    datafile = DataFile()
    section: Optional[Section] = datafile.NoneSection
    while file.not_end:
        predict = file.read_string(predict=True)

        if check_special_word(predict, datafile.Section):
            line = file.read_string()
            section = getattr(datafile, line.get_first_word())

            if section.__class__.__name__ == "SCHEDULE":
                __read_schedule_section(file, datafile)

        elif predict.get_first_word() in ("INCLUDE", "GDFILE"):
            read_path(file, datafile, section)

        elif predict.get_first_word() == "ARITHMETIC":
            read_arithmetic(file, datafile, section)

        elif check_special_word(predict, all_ecl_keyword):
            read_keyword(file, datafile, section)

        elif check_custom_cube(predict):
            read_custom_cube(file, datafile, section)

        elif predict.chek_skip():
            file.read_string()

        else:
            file.read_string()

    return datafile
"""
