from __future__ import annotations

from typing import Dict, Any


class EclipseBinaryData:
    pass


class BinaryData(EclipseBinaryData):
    def __init__(self, data: Dict[str, Any]) -> None:
        for key in data.keys():
            setattr(self, key, data[key])
