from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import Section

from HydrodynamicUtilities.Reader.ASCIIDataFileReader.BaseCreator import (
    BaseKeywordCreator,
)

from .RUNSPEC import RunspecKeywordCreator
from .GRID import GRIDConstructor

# from .EDIT import
from .PROPS import PROPSConstructor

# from .REGIONS import
# from .SOLUTION import
# from .SUMMARY import
# from .SCHEDULE import


def get_constructor(sections: Section) -> BaseKeywordCreator:
    name = sections.__class__.__name__
    if name in ("RUNSPEC", "UnInitializedRUNSPEC"):
        return RunspecKeywordCreator()
    elif name in ("GRID", "UnInitializedGRID"):
        return GRIDConstructor()
    elif name in ("PROPS", "UnInitializedPROPS"):
        return PROPSConstructor()
    else:
        return BaseKeywordCreator()
