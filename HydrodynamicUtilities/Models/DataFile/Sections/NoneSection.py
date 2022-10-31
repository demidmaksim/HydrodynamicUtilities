from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile import UnknownOneSlashWord, DataFile
    from typing import Callable

from .RUNSPEC import RUNSPEC
from .GRID import GRID
from .EDIT import EDIT
from .PROPS import PROPS
from .REGIONS import REGIONS
from .SOLUTION import SOLUTION
from .SUMMARY import SUMMARY
from .SCHEDULE import SCHEDULE
from HydrodynamicUtilities.Models.DataFile.Base import Section


class NoneSection(Section):
    def __init__(self, data_file: DataFile) -> None:
        super().__init__(data_file)
        self.__RUNSPEC = RUNSPEC
        self.__GRID = GRID
        self.__EDIT = EDIT
        self.__PROPS = PROPS
        self.__REGIONS = REGIONS
        self.__SOLUTION = SOLUTION
        self.__SUMMARY = SUMMARY
        self.__SCHEDULE = SCHEDULE

    def get_keyword(self, name: str) -> Callable:
        list_for_iter = (
            self.__RUNSPEC,
            self.__GRID,
            self.__EDIT,
            self.__PROPS,
            self.__REGIONS,
            self.__SOLUTION,
            self.__SUMMARY,
            self.__SCHEDULE,
        )

        kyword = None

        for section in list_for_iter:
            try:
                kyword = section.get_famous_keywords()[name]
                break
            except KeyError:
                pass

        if kyword is None:
            kyword = UnknownOneSlashWord
        return kyword
