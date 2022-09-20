from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Optional, Dict, Union, Type, Any


from ..Base import Section, Keyword, BaseKeywordCreator, UnknownKeyword
from ...Time.Point import TimePoint
from datetime import datetime
from ..ASCIIFile import ASCIIText
from copy import deepcopy


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
    ) -> None:
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
        nx: int = None,
        ny: int = None,
        nz: int = None,
    ) -> None:
        self.NX = nx
        self.NY = ny
        self.NZ = nz

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
    ) -> None:
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
    def __init__(self, data: Dict[str, Union[str, float, int]] = None) -> None:
        if data is not None:
            self.Data = data
        else:
            self.Data = dict()

    def append(self, data: DEFINESEntry) -> None:
        self.Data[data.Name] = data


class RunspecKeywordCreator(BaseKeywordCreator):
    def defines(self, data: ASCIIText) -> DEFINES:
        results = DEFINES()
        while not data.empty():
            row = data.to_slash(True, True)
            if row.empty():
                break

            list_row = row.split()

            name = list_row[0]
            value = list_row[1]

            try:
                min_value = list_row[2]
            except IndexError:
                min_value = None

            try:
                max_value = list_row[3]
            except IndexError:
                max_value = None

            try:
                var_type = list_row[4]
            except IndexError:
                var_type = None

            entry = DEFINESEntry(results, name, value, min_value, max_value, var_type)
            results.append(entry)
        return results

    def tabdims(self, data: ASCIIText) -> TABDIMS:
        data = data.replace_multiplication()
        sdata = data.to_slash()
        results = deepcopy(TABDIMS.get_base_value())
        for pid, pos in enumerate(sdata.split()):
            kw = list(TABDIMS.get_base_value().keys())[pid]
            results[kw] = pos
        return TABDIMS(**results)

    def vapoil(self, data: ASCIIText) -> VAPOIL:
        return VAPOIL()

    def disgas(self, data: ASCIIText) -> DISGAS:
        return DISGAS()

    def water(self, data: ASCIIText) -> WATER:
        return WATER()

    def oil(self, data: ASCIIText) -> OIL:
        return OIL()

    def gas(self, data: ASCIIText) -> GAS:
        return GAS()

    def start(self, data: ASCIIText) -> START:
        data = data.replace_multiplication()
        sdata = data.to_slash()
        results = deepcopy(START.get_base_value())
        for pid, pos in enumerate(sdata.split()):
            kw = list(START.get_base_value().keys())[pid]
            results[kw] = pos
        return START(**results)

    def metric(self, data: ASCIIText) -> METRIC:
        return METRIC()

    def dimens(self, data: ASCIIText) -> DIMENS:
        data = data.replace_multiplication()
        sdata = data.to_slash()
        results = deepcopy(DIMENS.get_base_value())
        for pid, pos in enumerate(sdata.split()):
            kw = list(DIMENS.get_base_value().keys())[pid]
            results[kw] = pos
        return DIMENS(**results)

    def create(self, data: str) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in RUNSPEC.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        fun = self.choose_fun(str(kw))
        return fun(adata)


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

    @classmethod
    def get_constructor(cls) -> Type[BaseKeywordCreator]:
        return RunspecKeywordCreator

    def get_start_date(self) -> Optional[TimePoint]:
        try:
            stat: START = getattr(self, "START")
            str_date = f"{stat.YEARS}-{stat.MONTH}-{stat.DAY}"
            date = datetime.strptime(str_date, "%Y-%b-%d")
            return TimePoint(date)
        except AttributeError:
            return None
