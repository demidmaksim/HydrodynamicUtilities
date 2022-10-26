from __future__ import annotations

import numpy as np
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Any, Tuple, Hashable
    from datetime import datetime

    valid_formats = Union[np.datetime64, str, datetime, Tuple[Any, ...]]

from datetime import datetime


class TimePoint:

    """
    %a	Сокращенное название дня недели
    %A	Полное название дня недели
    %b	Сокращенное название месяца
    %B	Полное название месяца
    %c	Дата и время
    %d	День месяца [01,31]
    %H	Час (24-часовой формат) [00,23]
    %I	Час (12-часовой формат) [01,12]
    %j	День года [001,366]
    %m	Номер месяца [01,12]
    %M	Число минут [00,59]
    %p	До полудня или после (при 12-часовом формате)
    %S	Число секунд [00,61]
    %U	Номер недели в году (нулевая неделя начинается с воскресенья) [00,53]
    %w	Номер дня недели [0(Sunday),6]
    %W	Номер недели в году (нулевая неделя начинается с понедельника) [00,53]
    %x	Дата
    %X	Время
    %y	Год без века [00,99]
    %Y	Год с веком
    %Z	Временная зона
    %%	Знак '%'
    """

    def __init__(self, date: valid_formats) -> None:
        self.Date: np.datetime64 = _to_datetime64(date)

    def __str__(self) -> str:
        return str(self.Date)

    def __repr__(self) -> str:
        return str(self.Date)

    def __eq__(self, other: TimePoint) -> bool:
        return self.Date == other.Date

    def __ne__(self, other: TimePoint) -> bool:
        return self.Date != other.Date

    def __lt__(self, other: TimePoint) -> bool:
        return self.Date < other.Date

    def __gt__(self, other: TimePoint) -> bool:
        return self.Date > other.Date

    def __le__(self, other: TimePoint) -> bool:
        return self.Date <= other.Date

    def __ge__(self, other: TimePoint) -> bool:
        return self.Date >= other.Date

    def __hash__(self) -> Hashable:
        return hash(self.Date)

    def to_datetime64(self) -> np.datetime64:
        return self.Date

    def to_str(self, str_format: str = "%Y-%m-%d %H:%M:%S") -> str:
        npdate = str(self.Date.astype(dtype="datetime64[s]"))
        str_date = datetime.strptime(npdate, "%Y-%m-%dT%H:%M:%S")
        return datetime.strftime(str_date, str_format)


def _to_datetime64(date: valid_formats) -> np.datetime64:
    if type(date) == np.datetime64:
        return date
    elif type(date) == str:
        return np.datetime64(date)
    elif type(date) == datetime:
        str_date = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
        return np.datetime64(str_date)
    elif isinstance(date, TimePoint):
        return date.to_datetime64()
    else:
        raise TypeError
