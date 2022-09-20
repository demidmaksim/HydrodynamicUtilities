from typing import List, Any, Union
from .Header import Header
import numpy as np


class Content:
    def __init__(self, header: Header, value: bytes) -> None:
        self.header: Header = header
        self.values: List[bytes] = [value]

    def __eq__(self, other: Any) -> bool:
        try:
            if self.header.keyword == other.header.keywords:
                return True
            else:
                return False
        except:
            return False

    @property
    def keyword(self) -> str:
        return self.header.keyword

    def append(self, value: bytes) -> None:
        self.values.append(value)

    def decode(self) -> Union[np.ndarray, List[str]]:
        number_obj = self.header.number_obj
        conv_format = self.header.ConvertorFormat
        length = self.header.length_one_obj

        data = b"".join(self.values)

        if conv_format != "c":
            arraydata: np.ndarray = np.frombuffer(data, dtype=">" + conv_format)
            if number_obj > 0 and len(arraydata) > 0:
                if int(len(arraydata) / number_obj) != 1:
                    dual = (int(len(arraydata) / number_obj), number_obj)
                    return np.reshape(arraydata, newshape=dual)
                else:
                    single = number_obj
                    return np.reshape(arraydata, newshape=single)

            else:
                return arraydata

        else:
            string = data.decode("utf-8")
            numwords = int(len(string) / length)
            return list(
                [string[w * length : (w + 1) * length].strip() for w in range(numwords)]
            )
