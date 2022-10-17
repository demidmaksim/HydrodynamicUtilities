from typing import Dict, Tuple, Optional, Iterator, Union, Type, List


class BaseKeyWord:
    Order: Tuple[str, ...] = ()
    MustToBe: Tuple[str, ...] = ()
    AdditionalControl: Optional[str] = None
    AdditionalMustToBe: Dict[str, Union[str, List[str], None]] = dict()
    XLSXPatern = Order
    ColumnType: Tuple[Type, ...] = (str,) * 100
    LastMulti = False


class OneRowKeyword(BaseKeyWord):
    Order: Tuple[str, ...] = ()
    MustToBe: Tuple[str, ...] = ()
    AdditionalControl: Optional[str] = None
    AdditionalMustToBe: Dict[str, Union[str, List[str], None]] = dict()
    XLSXPatern = Order
    ColumnType: Tuple[Type, ...] = (str,) * 100


class WELSPECS(OneRowKeyword):
    WellName = "Имя скважины"
    GroupName = "Группа скважины"
    IW = "IW"
    JW = "JW"
    ReferenceDepth = "Опорная глубина для забойного давления"
    PreferredPhase = "Предпочтительная фаза"
    DrainageRadius = "Радиус дренирования"
    SpecialInflowEquation = "Cпециальноe уравнениe притока"
    AutomaticClosing = "Aвтоматическое закрытие"
    BilateralFlows = "Возможность двусторонних перетоков"
    PressureTable = "Номер таблицы свойств в стволе скважины"
    CalculatingDensity = "Метод вычисления гидростатического напора"
    PressureCalculationMethod = "Способ расчета дебита в пластовых условиях"

    Order: Tuple[str, ...] = (
        WellName,
        GroupName,
        IW,
        JW,
        ReferenceDepth,
        PreferredPhase,
        DrainageRadius,
        SpecialInflowEquation,
        AutomaticClosing,
        BilateralFlows,
        PressureTable,
        CalculatingDensity,
        PressureCalculationMethod,
    )
    ColumnType = (
        str,
        str,
        float,
        int,
        int,
        str,
        float,
        str,
        str,
        str,
        int,
        str,
        str,
    )

    MustToBe = (WellName,)

    XLSXPatern = Order


class WELLTRACK(BaseKeyWord):
    SheetName = "WELLTRACK"

    WellName = "Имя скважины"
    BoreName = "Номер ствола"
    PointNumber = "Порядковый номер точки"
    X = "X"
    Y = "Y"
    Z = "Z"
    MD = "MD"

    Order = (
        WellName,
        BoreName,
        PointNumber,
        X,
        Y,
        Z,
        MD,
    )

    MustToBe = (
        WellName,
        BoreName,
        PointNumber,
        X,
        Y,
        Z,
        MD,
    )

    ColumnType = (
        str,
        int,
        int,
        float,
        float,
        float,
    )


class COMPDATMD(OneRowKeyword):
    WellName = "Имя скважины"
    Bore = "Номер ствола"
    FirstCutoff = "Первая отсечка перфорации"
    UpperLimit = "Верхний предел перфорации"
    DepthID = "Идентификатор значения глубины перфорации"
    PerforationStatus = "Статус перфорации"
    SaturationTable = "Номер таблицы насыщенности"
    ConductivityCoefficient = "Коэффициент проводимости"
    BoreholeDiameter = "Диаметр скважины"
    KH = "Величина KH"
    SKIN = "Cкин"
    DFactor = "D-фактор"
    ConductivityMultiplier = "Множитель коэффициента проводимости"
    PerforationType = "Тип перфорации"
    AutopsyNumber = "Номер вскрытия"

    Order = (
        WellName,
        Bore,
        FirstCutoff,
        UpperLimit,
        DepthID,
        PerforationStatus,
        SaturationTable,
        ConductivityCoefficient,
        BoreholeDiameter,
        KH,
        SKIN,
        DFactor,
        ConductivityMultiplier,
        PerforationType,
        AutopsyNumber,
    )

    ColumnType = (
        str,
        int,
        float,
        float,
        str,
        str,
        int,
        float,
        float,
        float,
        float,
        float,
        float,
        str,
        int,
    )

    MustToBe = (WellName,)

    XLSXPatern = Order


class WEFAC(OneRowKeyword):
    WellName = "Имя скважины"
    ServiceFactor = "Коэффициент эксплуатации"
    HZFactor = "Учет в расчете потоков ветвей и расширенной сети"

    Order = (
        WellName,
        ServiceFactor,
        HZFactor,
    )

    ColumnType = (
        str,
        float,
        str,
    )

    MustToBe = (
        WellName,
        ServiceFactor,
    )

    XLSXPatern = Order


class FRACTURE_SPECS(OneRowKeyword):
    WellName = "Имя скважины"
    Bore = "Ствол"
    FracName = "Имя трещины"
    MD = "MD"
    Azimuth = "Азимутальный угол"
    Antiaircraft = "Зенитный угол"
    LeftHalfLength = "Левая полудлина"
    RightHalfLength = "Правая полудлина"
    Height1 = "Высота трещины в первом направлении"
    Height2 = "Высота трещины во втором направлении"
    Width = "Ширина трещины FZ"
    CrackAffectedZoneWidth = "Ширина зоны влияния трещины"
    CrackBoundaryCurvature = "Кривизна границы трещины"
    ReservoirPermeabilityMultiplier = "Множитель проницаемости пласта"
    Permeability = "Проницаемость"
    CrackImpactPermeability = "Проницаемость в зоне влияния трещины (NFZ)"
    MatrixPermeability = "Проницаемость трещины (Матрицы)"
    CrackImpactPermeability2 = "Проницаемость в зоне влияния трещины (NFZ2)"
    FractureProductivityMultiplier = "Множитель продуктивности трещины"
    ProppantTypeName = "Название типа пропанта"
    ProppantProperties = "Xарактеристика падения проницаемости"
    FallPeriod = "Период падения проницаемости в трещине"
    FlowModel = "Имя функции зависимости проницаемости трещины от времени"

    Order = (
        WellName,
        Bore,
        FracName,
        MD,
        Azimuth,
        Antiaircraft,
        LeftHalfLength,
        RightHalfLength,
        Height1,
        Height2,
        Width,
        CrackAffectedZoneWidth,
        CrackBoundaryCurvature,
        ReservoirPermeabilityMultiplier,
        Permeability,
        CrackImpactPermeability,
        MatrixPermeability,
        CrackImpactPermeability2,
        FractureProductivityMultiplier,
        ProppantTypeName,
        ProppantProperties,
        FallPeriod,
        FlowModel,
    )

    ColumnType = (
        str,
        int,
        str,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
    )

    MustToBe = (
        WellName,
        FracName,
        MD,
        LeftHalfLength,
        RightHalfLength,
        Height1,
        Height2,
        Width,
    )

    XLSXPatern = Order


class FRACTURE_STAGE(OneRowKeyword):
    FracName = "Имя трещины"
    FrackState = "Состояние"
    ArithmeticName = "Имя арифметики"
    ProppantVolume = "Объем пропанта"

    Order = (
        FracName,
        FrackState,
        ArithmeticName,
        ProppantVolume,
    )

    ColumnType = (
        str,
        str,
        str,
        float,
    )

    MustToBe = (FrackState,)

    XLSXPatern = Order


class WCONPROD(OneRowKeyword):

    WellName = "Имя скважины"
    OperatingModes = "Режимы работы"  # open/close
    WellControl = "Управление скважиной"
    OilFlowRate = "Дебит нефти"
    WaterFlowRate = "Дебит воды"
    GasFlowRate = "Дебит газа"
    LiquidFlowRate = "Дебит жидкости"
    FlowInReservoir = "Дебит флюида в пластовых условиях"
    BHP = "Забойное давление"
    THP = "Устьевое давление"
    VFP = "Номер таблицы VFP"
    ALQ = "Величина ALQ"
    WetGasRate = "Дебит жирного газа"
    MolarFlowRate = "Молярный дебит"
    SteamRate = "Дебит пара"
    PressureShift = "Сдвиг давления"
    TemperatureShift = "Сдвиг температуры"
    ThermalFlowRate = "Тепловой дебит"
    LinearCombination = "Линейная комбинация"
    NGLProduction = "Дебит ШФЛУ"

    Order = (
        WellName,
        OperatingModes,
        WellControl,
        OilFlowRate,
        WaterFlowRate,
        GasFlowRate,
        LiquidFlowRate,
        FlowInReservoir,
        BHP,
        THP,
        VFP,
        ALQ,
        WetGasRate,
        MolarFlowRate,
        SteamRate,
        PressureShift,
        TemperatureShift,
        ThermalFlowRate,
        LinearCombination,
        NGLProduction,
    )

    ColumnType = (
        str,
        str,
        str,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        int,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
    )

    MustToBe = (
        WellName,
        OperatingModes,
        WellControl,
    )

    AdditionalControl = WellControl

    AdditionalMustToBe = {
        "LRAT": LiquidFlowRate,
        "ORAT": OilFlowRate,
        "WRAT": WaterFlowRate,
        "GRAT": GasFlowRate,
        "WGRA": WetGasRate,
        "RESV": FlowInReservoir,
        "THP": THP,
        "BHP": BHP,
        "TMRA": MolarFlowRate,
        "STRA": SteamRate,
        "SATP": None,
        "SATT": None,
        "CVAL": ThermalFlowRate,
        "NGL": NGLProduction,
        "GRUP": None,
    }

    XLSXPatern = Order


class WECON(OneRowKeyword):

    WellName = "Имя скважины"
    LowerOilRate = "Нижний экономический предел по дебиту нефти"
    LowerGasRate = "Нижний экономический предел по дебиту газа"
    UpperWCT = "Верхний экономический предел по обводненности"
    UpperGOR = "Верхний экономический предел по газовому фактору"
    UpperWaterInGas = "Верхний экономический предел по содержанию воды в газе"
    WCTOperation = "Выполняемая операция при превышении предела обводненности"
    EndCalculation = "Флаг, задающий конец расчета модели"
    OpenWell = "Имя замещающей скважины"
    EconLimitation = "Показатель минимального экономического ограничения"
    WCTLimitation = "Вторичное ограничение по максимальной обводненности"
    WCTLimitationOperation = (
        "Операция при превышении вторичного ограничения обводненности"
    )
    UpperGasInLiquid = "Верхний предел по содержанию газа в жидкости"
    LowerLiqud = "Нижний экономический предел по дебиту жидкости"

    Order = (
        WellName,
        LowerOilRate,
        LowerGasRate,
        UpperWCT,
        UpperGOR,
        UpperWaterInGas,
        WCTOperation,
        EndCalculation,
        OpenWell,
        EconLimitation,
        WCTLimitation,
        WCTLimitationOperation,
        UpperGasInLiquid,
        LowerLiqud,
    )

    ColumnType = (
        str,
        float,
        float,
        float,
        float,
        float,
        str,
        str,
        str,
        str,
        float,
        str,
        float,
        float,
    )

    MustToBe = (WellName,)

    XLSXPatern = Order


class WCONINJE(OneRowKeyword):

    WellName = "Имя скважины"
    FluidType = "Тип закачиваемого флюида"
    OperatingModes = "Режим работы скважины"  # open/close
    WellControl = "Управление скважиной"
    VolumeInPlace = "Объем закачки в поверхностных условиях"
    VolumeInReservoir = "Объем закачки в пластовых условиях"
    BHP = "Забойное давление"
    THP = "Устьевое давление"
    VFR = "номер VFP"
    OilInFluid = "Концентрация нефти в нагнетаемом флюиде"
    OilInRate = "Доля нефти в потоке нагнетания"
    WaterInRate = "Доля воды в потоке нагнетания"
    GasInRate = "Доля газа в потоке нагнетания"

    Order = (
        WellName,
        FluidType,
        OperatingModes,
        WellControl,
        VolumeInPlace,
        VolumeInReservoir,
        BHP,
        THP,
        VFR,
        OilInFluid,
        OilInRate,
        WaterInRate,
        GasInRate,
    )

    ColumnType = (
        str,
        str,
        str,
        str,
        float,
        float,
        float,
        float,
        int,
        float,
        float,
        float,
        float,
    )

    MustToBe = (
        WellName,
        FluidType,
        OperatingModes,
        WellControl,
    )

    AdditionalControl = WellControl

    AdditionalMustToBe = {
        "RATE": VolumeInPlace,
        "THP": THP,
        "BHP": BHP,
        "RESV": VolumeInReservoir,
        "GRUP": None,
    }

    XLSXPatern = Order


class WECONINJ(OneRowKeyword):

    WellName = "Имя скважины"
    LowerEconomic = "Нижний экономический предел объема закачки"

    Order = (
        WellName,
        LowerEconomic,
    )

    ColumnType = (
        str,
        float,
    )

    MustToBe = (WellName,)

    XLSXPatern = Order


class WELDRAW(OneRowKeyword):

    WellName = "Имя скважины"
    MaxDrow = "Максимально допустимая депрессия"
    Phase = "Фаза"
    DrowLimit = "Учет ограничения депрессии при расчете потенциала добычи"
    TypeLimit = "Ограничивается ли взвешенное по индексу продуктивности PI"

    Order = (
        WellName,
        MaxDrow,
        Phase,
        DrowLimit,
        TypeLimit,
    )

    ColumnType = (
        str,
        float,
        str,
        float,
        str,
    )

    MustToBe = (
        WellName,
        MaxDrow,
    )

    XLSXPatern = Order


class GCONPROD(OneRowKeyword):

    GroupName = "Имя группы"
    ControlType = "Тип контроля"
    OilRate = "Дебит нефти"
    WaterRate = "Дебит воды"
    GasRate = "Дебит газа"
    LiquidRate = "Дебит жидкости"
    LimitOpertion = "Выполняемая операция при превышении"
    GroupToGroup = "Может ли дебит группы контролироваться группой"
    DirectionalRate = "Направляющий дебит группы"
    Phase = "Фаза, для которой применяется предыдущий параметр"
    WatLimitOperation = "Операция при превышении ограничения на дебит воды"
    GasLimitOperation = "Операция при превышении ограничения на дебит газа"
    LiqLimitOperation = "Операция при превышении ограничения на дебит жидкости"
    FluidInReservoir = "Дебит флюида в пластовых условиях"
    BalancingProportion = "Значение уравновешивающей доли отбора."
    WetGasRate = "Дебит жирного газа"
    HeatFlow = "Заданный дебит теплоты"
    GasInPlace = "Доля дебита газа в поверхностных условиях"
    WaterInPlace = "Доля дебита воды в поверхностных условиях"

    Order = (
        GroupName,
        ControlType,
        OilRate,
        WaterRate,
        GasRate,
        LiquidRate,
        LimitOpertion,
        GroupToGroup,
        DirectionalRate,
        Phase,
        WatLimitOperation,
        GasLimitOperation,
        LiqLimitOperation,
        FluidInReservoir,
        BalancingProportion,
        WetGasRate,
        HeatFlow,
        GasInPlace,
        WaterInPlace,
    )

    ColumnType = (
        str,
        str,
        float,
        float,
        float,
        float,
        str,
        str,
        float,
        str,
        str,
        str,
        str,
        float,
        float,
        float,
        float,
        float,
        float,
    )

    MustToBe = (
        GroupName,
        ControlType,
    )

    AdditionalControl = ControlType

    AdditionalMustToBe = {
        "NONE": None,
        "LRAT": LiquidRate,
        "ORAT": OilRate,
        "WRAT": WaterRate,
        "GRAT": GasRate,
        "RESV": FluidInReservoir,
        "PRBL": BalancingProportion,
        "WGRA": WetGasRate,
        "PBGS": GasInPlace,
        "PBWS": WaterInPlace,
        "FLD": None,
    }

    XLSXPatern = Order


class GCONINJE(OneRowKeyword):

    GroupName = "Имя группы"
    FluidType = "Тип закачиваемого флюида"
    ControlType = "Тип контроля"
    VolumeInPlace = "Объем закачки в поверхностных условиях"
    VolumeInReservoir = "Объем закачки в пластовых условиях"
    TargetReInjection = "Целевой коэффициент повторной закачки"
    TargetCompensationFactor = "Целевой коэффициент компенсации"
    GroupToGroup = "Может ли дебит группы контролироваться группой"
    DirectionalRate = "Направляющий дебит группы"
    DirectionalRateType = "Тип направляющего дебита для предыдущего параметра"
    GroupNameForBack = "Имя группы для контроля доли дебита для ре-закачки"
    GroupNameForReplac = "Имя группы для контроля доли отбора для ре-закачки"

    Order = (
        GroupName,
        FluidType,
        ControlType,
        VolumeInPlace,
        VolumeInReservoir,
        TargetReInjection,
        TargetCompensationFactor,
        GroupToGroup,
        DirectionalRate,
        DirectionalRateType,
        GroupNameForBack,
        GroupNameForReplac,
    )

    ColumnType = (
        str,
        str,
        str,
        float,
        float,
        float,
        float,
        str,
        float,
        str,
        str,
        str,
    )

    MustToBe = (
        GroupName,
        FluidType,
        ControlType,
    )

    AdditionalControl = ControlType

    AdditionalMustToBe = {
        "NONE": None,
        "RATE": VolumeInPlace,
        "RESV": VolumeInReservoir,
        "REIN": TargetReInjection,
        "VREP": TargetCompensationFactor,
    }

    XLSXPatern = Order


class WSEGVALV(OneRowKeyword):

    WellName = "Имя скважины"
    Segment = "Номер сегмента"
    FlowRateCoef = "Коэффициент расхода для клапана"
    CrossSectionalAreaFlow = "Площадь поперечного сечения для потока"
    AdditionalPipeLength = "Дополнительная длина трубы"
    PipeDiameter = "Диаметр трубы"
    AbsoluteRoughness = "Абсолютная шероховатость"
    CrossSectionalAreaPipe = "Площадь поперечного сечения трубы"
    Mode = "Статус"  # Open/close
    MaxCrossSectionalArea = "Максимальная площадь поперечного сечения"

    Order = (
        WellName,
        Segment,
        FlowRateCoef,
        CrossSectionalAreaFlow,
        AdditionalPipeLength,
        PipeDiameter,
        AbsoluteRoughness,
        CrossSectionalAreaPipe,
        Mode,
        MaxCrossSectionalArea,
    )

    ColumnType = (
        str,
        int,
        float,
        float,
        float,
        float,
        float,
        float,
        str,
        float,
    )

    MustToBe = (
        WellName,
        Segment,
        FlowRateCoef,
        CrossSectionalAreaFlow,
    )

    XLSXPatern = Order


class WCONHIST(OneRowKeyword):

    WellName = "Имя скважины"
    OperatingModes = "Режимы работы"  # open/close
    WellControl = "Управление скважиной"
    OilFlowRate = "Дебит нефти"
    WaterFlowRate = "Дебит воды"
    GasFlowRate = "Дебит газа"
    VFP = "Номер таблицы VFP"
    ALQ = "Величина ALQ"
    THP = "Устьевое давление"
    BHP = "Забойное давление"
    WetGasRate = "Дебит жирного газа"
    NGLProduction = "Дебит ШФЛУ"

    Order = (
        WellName,
        OperatingModes,
        WellControl,
        OilFlowRate,
        WaterFlowRate,
        GasFlowRate,
        VFP,
        ALQ,
        THP,
        BHP,
        WetGasRate,
        NGLProduction,
    )

    ColumnType = (
        str,
        str,
        str,
        float,
        float,
        float,
        int,
        float,
        float,
        float,
        float,
        float,
    )

    MustToBe = (
        WellName,
        OperatingModes,
        WellControl,
        OilFlowRate,
        WaterFlowRate,
        GasFlowRate,
    )

    AdditionalControl = WellControl

    AdditionalMustToBe = {
        "LRAT": [OilFlowRate, WaterFlowRate],
        "ORAT": OilFlowRate,
        "WRAT": WaterFlowRate,
        "GRAT": GasFlowRate,
        "WGRA": WetGasRate,
        "NGL": NGLProduction,
        "RESV": [OilFlowRate, WaterFlowRate, GasFlowRate],
        "BHP": BHP,
        "THP": THP,
        "TGRUP": None,
        "NONE": None,
    }

    XLSXPatern = Order


class WCONINJH(OneRowKeyword):

    WellName = "Имя скважины"
    FluidType = "Тип закачиваемого флюида"
    OperatingModes = "Режим работы скважины"  # open/close
    VolumeInPlace = "Объем закачки в поверхностных условиях"
    BHP = "Забойное давление"
    THP = "Устьевое давление"
    VFR = "номер VFP"
    OilInFluid = "Концентрация нефти в нагнетаемом флюиде"
    OilInRate = "Доля нефти в потоке нагнетания"
    WaterInRate = "Доля воды в потоке нагнетания"
    GasInRate = "Доля газа в потоке нагнетания"
    WellControl = "Режим контроля скважины:"

    Order = (
        WellName,
        FluidType,
        OperatingModes,
        VolumeInPlace,
        BHP,
        THP,
        VFR,
        OilInFluid,
        OilInRate,
        WaterInRate,
        GasInRate,
        WellControl,
    )

    ColumnType = (
        str,
        str,
        str,
        float,
        float,
        float,
        int,
        float,
        float,
        float,
        float,
        str,
    )

    MustToBe = (
        WellName,
        FluidType,
        OperatingModes,
        WellControl,
    )

    AdditionalControl = WellControl

    AdditionalMustToBe = {
        "RATE": VolumeInPlace,
        "THP": THP,
        "BHP": BHP,
    }

    XLSXPatern = Order


class WELOPEN(OneRowKeyword):

    __Name = "Имя скважины"
    __Status = "Статус"
    __i = "i"
    __j = "j"
    __k = "k"
    __FirstOpeningNumber = "Номер первого вскрытия"
    __NumberOfLastOpening = "Номер последнего вскрытия"

    Order = (
        __Name,
        __Status,
        __i,
        __j,
        __k,
        __FirstOpeningNumber,
        __NumberOfLastOpening,
    )

    MustToBe = (
        __Name,
        __Status,
    )


class WLIST(OneRowKeyword):

    __GroupName = "Имя списка скважин"
    __Action = "Действие"
    __Name = "Имя скважы"

    Order = (
        __GroupName,
        __Action,
        __Name,
    )

    MustToBe = (
        __GroupName,
        __Action,
        __Name,
    )

    LastMulti = True


class GRUPTREE(OneRowKeyword):

    __ChildGroup = "Имя дочерней группы"
    __ParentGroup = "Имя материнской группы"

    Order = (
        __ChildGroup,
        __ParentGroup,
    )

    MustToBe = (
        __ChildGroup,
        __ParentGroup,
    )


class ARITHMETIC(OneRowKeyword):

    __Expression = "Формула"
    Order = (__Expression,)

    MustToBe = (__Expression,)


class GINJGAS(OneRowKeyword):
    GroupName = "Имя группы"
    GasCompound = "Cостав нагнетаемого газа"
    CharacterString = "Строка символов, задающая данные в параметре 2"
    CompoundName = "Имя композиционного состава потока"
    Separator = "Ступень сепаратора"

    Order = (
        GroupName,
        GasCompound,
        CharacterString,
        CompoundName,
        Separator,
    )


class Comment(BaseKeyWord):
    Comment = "Комминтарий"

    Order = (Comment,)


class ArbitraryWord(BaseKeyWord):
    KeyWordName = "Ключевое слово"
    KeyWordValue = "Строка с управляющим словами"

    Order = (
        KeyWordName,
        KeyWordValue,
    )


class WELTARG(OneRowKeyword):
    WellName = "Имя скважины"
    Control = "Контроль"
    Value = "Новое значение"

    Order = (
        WellName,
        Control,
        Value,
    )


class WGRUPCON(OneRowKeyword):
    WellName = "Имя скважины"
    GroupControl = "Ставится ли скважина под групповое управление"
    FlowRate = "Направляющий дебит"
    Phase = "Фаза"
    Multiplier = "Множитель направляющего дебита"

    Order = (
        WellName,
        GroupControl,
        FlowRate,
        Phase,
        Multiplier,
    )


class WTEST(OneRowKeyword):
    WellName = "Имя скважины/списка"
    CheckInterval = "Интервал проверки"
    ClosingCondition = "Условие закрытия"
    InspectionsNumber = "Количество проверок скважины"
    StartTime = "Время запуска"

    Order = (
        WellName,
        CheckInterval,
        ClosingCondition,
        InspectionsNumber,
        StartTime,
    )


class WVFPEXP(OneRowKeyword):
    WellName = "Имя скважины"
    Method = "Метод"
    CLoseWellFlag = "Закрыть скважину"
    THPControlFlag = "Переход к управлению по THP"
    ExtrapolateMethod = "Cпособ экстраполяции значений"

    Order = (
        WellName,
        Method,
        CLoseWellFlag,
        THPControlFlag,
        ExtrapolateMethod,
    )


class COMPDAT(OneRowKeyword):
    WellName = "Имя скважины"
    Xcoord = "Координата участка перфорации по оси X"
    Ycoord = "Координата участка перфорации по оси Y"
    Z1coord = "Cлой, с которого начинается вертикальный"
    Z2coord = "Cлой, на котором заканчивается вертикальный участок перфорации"
    PerforationStatus = "Статус перфорации"
    SaturationTable = "Номер таблицы насыщенности"
    ConductivityCoefficient = "Коэффициент проводимости"
    BoreholeDiameter = "Диаметр скважины"
    KH = "Величина KH"
    SKIN = "Cкин"
    DFactor = "D-фактор"
    SpatialOrientation = "Пространственная ориентация скважины"
    Radius = "Эффективный радиус"

    Order = (
        WellName,
        Xcoord,
        Ycoord,
        Z1coord,
        Z2coord,
        PerforationStatus,
        SaturationTable,
        ConductivityCoefficient,
        BoreholeDiameter,
        KH,
        SKIN,
        DFactor,
        SpatialOrientation,
        Radius,
    )


class ScheduleKeyword:
    keyword: Dict[str, Type[BaseKeyWord]] = {
        WELSPECS.__name__: WELSPECS,
        WELLTRACK.__name__: WELLTRACK,
        COMPDAT.__name__: COMPDAT,
        COMPDATMD.__name__: COMPDATMD,
        FRACTURE_SPECS.__name__: FRACTURE_SPECS,
        FRACTURE_STAGE.__name__: FRACTURE_STAGE,
        WEFAC.__name__: WEFAC,
        WECON.__name__: WECON,
        WECONINJ.__name__: WECONINJ,
        WCONPROD.__name__: WCONPROD,
        WCONINJE.__name__: WCONINJE,
        WELDRAW.__name__: WELDRAW,
        GCONPROD.__name__: GCONPROD,
        GCONINJE.__name__: GCONINJE,
        WSEGVALV.__name__: WSEGVALV,
        WCONHIST.__name__: WCONHIST,
        WCONINJH.__name__: WCONINJH,
        WLIST.__name__: WLIST,
        WELOPEN.__name__: WELOPEN,
        GRUPTREE.__name__: GRUPTREE,
        ARITHMETIC.__name__: ARITHMETIC,
        GINJGAS.__name__: GINJGAS,
        Comment.__name__: Comment,
        ArbitraryWord.__name__: ArbitraryWord,
        WELTARG.__name__: WELTARG,
        WGRUPCON.__name__: WGRUPCON,
        WTEST.__name__: WTEST,
        WVFPEXP.__name__: WVFPEXP,
    }

    Order = (
        Comment,
        WELSPECS,
        WELLTRACK,
        COMPDATMD,
        COMPDAT,
        WSEGVALV,
        FRACTURE_SPECS,
        FRACTURE_STAGE,
        WEFAC,
        WECON,
        WECONINJ,
        WCONPROD,
        WCONINJE,
        WGRUPCON,
        WELDRAW,
        GCONPROD,
        GCONINJE,
        WCONHIST,
        WCONINJH,
        WLIST,
        WELOPEN,
        GRUPTREE,
        ARITHMETIC,
        GINJGAS,
        ArbitraryWord,
        WELTARG,
        WTEST,
        WVFPEXP,
    )

    ForWrite = (
        Comment,
        WELSPECS,
        WELLTRACK,
        COMPDATMD,
        COMPDAT,
        WSEGVALV,
        FRACTURE_SPECS,
        FRACTURE_STAGE,
        WEFAC,
        WECON,
        WECONINJ,
        WCONPROD,
        WCONINJE,
        WGRUPCON,
        WELDRAW,
        GCONPROD,
        GCONINJE,
        WCONHIST,
        WCONINJH,
        WLIST,
        WELOPEN,
        GRUPTREE,
        ARITHMETIC,
        GINJGAS,
        ArbitraryWord,
        WELTARG,
        WTEST,
        WVFPEXP,
    )

    @classmethod
    def __getitem__(cls, item: str) -> Type[BaseKeyWord]:
        return cls.keyword[item]

    def __contains__(self, item: str) -> bool:
        return item in self.keys()

    @classmethod
    def iter(cls) -> Iterator[Type[BaseKeyWord]]:
        for keyword in cls.Order:
            yield keyword

    @classmethod
    def keys(cls) -> List[str]:
        return list(cls.keyword.keys())
