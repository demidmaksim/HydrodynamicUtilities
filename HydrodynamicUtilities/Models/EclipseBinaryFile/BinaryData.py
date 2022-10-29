from __future__ import annotations

from typing import Dict, Any, List


class EclipseBinaryData:
    pass


class BinaryData(EclipseBinaryData):
    def __init__(self, data: Dict[str, Any]) -> None:
        for key in data.keys():
            self.__setattr__(key, data[key])

    def __getattr__(self, item: str) -> Any:
        return super().__getattribute__(item)

    def keys(self) -> List[str]:
        return list(self.__dict__)
