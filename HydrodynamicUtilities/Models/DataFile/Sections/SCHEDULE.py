from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.DataFile import DataFile


from ..Base import Section, UnknownKeyword
from HydrodynamicUtilities.Models.Strategy.Frame import ScheduleDataframe

from HydrodynamicUtilities.Models.Source.EtNKW_crutch import data

# relative_path = "../../Models/Source/Eclipse_tNavigator.kwd"
# path = Path(os.path.abspath(__file__)).parent / relative_path
# all_ecl_keyword = pd.read_csv(path, header=None).iloc[:, 0].to_list()

all_ecl_keyword = data


class DirtySchData(UnknownKeyword):
    def __init__(
        self,
        keyword_name: str,
        method: str = "read",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(method, *args, **kwargs)
        self.Name = keyword_name

    def __repr__(self) -> str:
        return self.Name


class SCHEDULE(Section):
    def __init__(self, data_file: DataFile) -> None:
        super().__init__(data_file)
        self.SDF = ScheduleDataframe()
        self.DirtyData = []
        self.Dates = None
