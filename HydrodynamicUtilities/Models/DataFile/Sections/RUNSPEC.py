from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Optional, Dict, Union, Type, Any

from ..Base import Section, UnInitializedSection, Keyword
from ...Time.Point import TimePoint
from datetime import datetime


class VAPOIL(Keyword):
    pass


class DISGAS(Keyword):
    pass


class WATER(Keyword):
    pass


class OIL(Keyword):
    pass


class GAS(Keyword):
    pass


class METRIC(Keyword):
    pass


class START(Keyword):

    __Order = {
        "day": None,
        "month": None,
        "years": None,
    }

    def __init__(
        self,
        day: str = 1,
        month: str = "JAN",
        years: str = 1900,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.DAY = day
        self.MONTH = month
        self.YEARS = years

    def __repr__(self) -> str:
        return f"{self.YEARS}-{self.MONTH}-{self.DAY}"

    @classmethod
    def get_base_value(cls) -> Dict[str, Any]:
        return cls.__Order


class DIMENS(Keyword):

    __Order = {
        "nx": None,
        "ny": None,
        "nz": None,
    }

    def __init__(
        self,
        nx: int,
        ny: int,
        nz: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.NX = nx
        self.NY = ny
        self.NZ = nz

    def get_statistic(self) -> str:
        total_cells = self.NX * self.NY * self.NZ
        try:
            datafile = self.ParentSection.get_data_file()
            actnnum_cell = datafile.GRID.Cubs.ACTNUM.Data.sum()
        except AttributeError:
            actnnum_cell = self.NX * self.NY * self.NZ

        share = actnnum_cell / total_cells * 100

        results = (
            f"NX: {self.NX}\n"
            f"NY: {self.NY}\n"
            f"NZ: {self.NZ}\n"
            f"Total cells: {total_cells}\n"
            f"Active cell: {actnnum_cell} ({round(share, 2)}%)\n"
        )
        return results

    def get_total_cells(self) -> int:
        return self.NX * self.NY * self.NZ

    @classmethod
    def get_base_value(cls) -> Dict[str, Any]:
        return cls.__Order


class TABDIMS(Keyword):

    __Order = {
        "satnum": 1,
        "pvtnum": 1,
        "max_rpp_table": 20,
        "max_pvt_table": 20,
        "fipnum": 1,
        "max_gor_table": 20,
        "max_ogr_table": 20,
        "max_enptvt": 1,
        "eosnum": 1,
        "number_regions_equation": 1,
        "flux_region": None,
        "thermal_regions": None,
        "rock_property_tables": 14,
        "pressure_regions": None,
        "max_temperature_number": None,
        "transport_regions": None,
    }

    def __init__(
        self,
        satnum: int = 1,
        pvtnum: int = 1,
        max_rpp_table: int = 20,
        max_pvt_table: int = 20,
        fipnum: int = 1,
        max_gor_table: int = 20,
        max_ogr_table: int = 20,
        max_enptvt: int = 1,
        eosnum: int = 1,
        number_regions_equation: int = 1,
        flux_region: int = None,
        thermal_regions: int = None,
        rock_property_tables: int = 14,
        pressure_regions: int = None,
        max_temperature_number: int = None,
        transport_regions: int = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.SATNUM: int = satnum
        self.PVTNUM: int = pvtnum
        self.MaxRPPTable: int = max_rpp_table
        self.MaxPVTTable: int = max_pvt_table
        self.FIPNUM: int = fipnum
        self.MaxGORTable: int = max_gor_table
        self.MaxOGRTable: int = max_ogr_table
        self.MaxENPTVT: int = max_enptvt
        self.EOSNUM: int = eosnum
        self.NumberRegionsEquation: int = number_regions_equation
        self.FLUXRegion: int = flux_region
        self.ThermalRegions: int = thermal_regions
        self.RockPropertyTables: int = rock_property_tables
        self.PressureRegions: int = pressure_regions
        self.MaxTemperatureNumber: int = max_temperature_number
        self.TransportRegions: int = transport_regions

    @classmethod
    def get_base_value(cls) -> Dict[str, Any]:
        return cls.__Order


class DEFINESEntry:
    def __init__(
        self,
        defines: DEFINES,
        name: str,
        value: Union[str, float, int],
        min_value: Union[float, int] = None,
        max_value: Union[float, int] = None,
        var_type: str = "REAL",
    ) -> None:
        self.__DEFINES = defines
        self.Name = name
        self.Value = value
        self.MaxValue = max_value
        self.MinValue = min_value
        self.VarType = var_type

    def __repr__(self) -> str:
        return (
            f"{self.Name} {self.Value} {self.MinValue} {self.MaxValue} {self.VarType}"
        )


class DEFINES(Keyword):
    def __init__(
        self,
        data: Dict[str, Union[str, float, int]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if data is not None:
            self.Data = data
        else:
            self.Data = dict()

    def append(self, data: DEFINESEntry) -> None:
        self.Data[data.Name] = data


class RUNSPEC(Section):
    __Keyword: Dict[str, Type[Keyword]] = {
        "TABDIMS": TABDIMS,
        "VAPOIL": VAPOIL,
        "DISGAS": DISGAS,
        "WATER": WATER,
        "OIL": OIL,
        "GAS": GAS,
        "START": START,
        "METRIC": METRIC,
        "DIMENS": DIMENS,
        "DEFINES": DEFINES,
    }

    __FamousKeyword = tuple(__Keyword.keys())

    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return cls.__Keyword

    def get_start_date(self) -> Optional[TimePoint]:
        try:
            stat: START = getattr(self, "START")
            str_date = f"{stat.YEARS}-{stat.MONTH}-{stat.DAY}"
            date = datetime.strptime(str_date, "%Y-%b-%d")
            return TimePoint(date)
        except AttributeError:
            return None


class UnInitializedRUNSPEC(UnInitializedSection):
    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return RUNSPEC.get_famous_keyword()
