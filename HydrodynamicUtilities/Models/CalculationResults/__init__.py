from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..EclipseBinaryFile import SUMMARY, EclipseBinaryData
    from typing import List, Union, Tuple


from .CRdataframe import CalcResults, PeriodCalcResults
from ..EclipseBinaryFile import SUMMARY


def __create_from_summary(
    data: SUMMARY,
    param_list: Union[List[str], Tuple[str, ...]],
) -> CalcResults:
    results = CalcResults()

    for param in param_list:
        part_of_data = data.get(param)
        for vector in part_of_data:
            if vector.shape[0] == 0 or vector.shape[1] == 0:
                pass
            else:
                cn = data.CalcName
                name = vector.Header.Names[0]
                key = vector.Header.Keywords[0]
                num = vector.Header.Num[0]
                unit = vector.Header.Unit[0]
                time = vector.TimeVector
                value = vector.values.T[0]
                results.append(cn, name, key, num, unit, time, value)

    return results


def __crete_from_many_summary(
    data_list: Union[List[EclipseBinaryData], Tuple[EclipseBinaryData]],
    param_list: Union[List[str], Tuple[str, ...]],
) -> CalcResults:
    results = CalcResults()

    for data in data_list:
        if isinstance(data, SUMMARY):
            value = __create_from_summary(data, param_list)
            results.extend(value)
        else:
            print(f"file: {data} skip")

    return results


def create_from_summary(
    data: Union[SUMMARY, Union[List[EclipseBinaryData], Tuple[EclipseBinaryData]]],
    param_list: Union[List[str], Tuple[str, ...]],
) -> CalcResults:
    if isinstance(data, SUMMARY):
        return __create_from_summary(data, param_list)
    elif isinstance(data, (list, tuple)):
        return __crete_from_many_summary(data, param_list)
    else:
        raise TypeError
