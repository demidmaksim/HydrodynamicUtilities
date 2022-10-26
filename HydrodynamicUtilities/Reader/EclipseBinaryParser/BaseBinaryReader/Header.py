from struct import unpack
from typing import BinaryIO, Any, Dict, Tuple


class Header:
    def __init__(
        self,
        keyword: str,
        number_of_objects: int,
        ecl_format: str,
        length: int,
        convertor_format: str,
    ) -> None:

        self.keyword: str = keyword
        self.number_obj: int = number_of_objects
        self.EclipseFormat: str = ecl_format
        self.length_one_obj: int = length
        self.ConvertorFormat: str = convertor_format

    def __eq__(self, other: Any) -> bool:
        try:
            if self.keyword == other.keywords:
                return True
            else:
                return False
        except:
            return False

    @property
    def length_block(self) -> int:
        return self.length_one_obj * self.number_obj


class BinaryHeaderWorker:

    length_header: int = 24  # 24 is size of header
    significant_byte: int = 16  # 16 is size significant byte area of header

    lengths: Dict[str, int] = {
        "INTE": 4,
        "LOGI": 4,
        "REAL": 4,
        "CHAR": 8,
        "DOUB": 8,
        "MESS": 8,
    }

    formats: Dict[str, str] = {
        "INTE": "i",
        "LOGI": "?",
        "REAL": "f",
        "CHAR": "c",
        "DOUB": "d",
        "MESS": "c",
    }


class BinaryHeaderReader(BinaryHeaderWorker):
    @classmethod
    def __byte_init(cls, ecl_format: str) -> Tuple[int, str]:
        if ecl_format in cls.formats.keys():
            length_one_obj = cls.lengths[ecl_format]
            convertor_format = cls.formats[ecl_format]

        elif ecl_format[:2] == "C0":
            length_one_obj = int(ecl_format[2:])
            convertor_format = "c"

        else:
            raise NameError("HiThere")

        return length_one_obj, convertor_format

    @classmethod
    def __header_from_bytes(cls, data: bytes) -> Header:

        keyword = str(data[4:12], "utf-8").strip()
        numobjec = unpack(">i", data[12:16])[0]
        datatype = str(data[16:20], "utf-8")
        length, dattyp = cls.__byte_init(datatype)
        header = Header(keyword, numobjec, datatype, length, dattyp)

        return header

    @classmethod
    def header_from_file(cls, file: BinaryIO) -> Header:
        binary_header = file.read(cls.length_header)
        return cls.__header_from_bytes(binary_header)


class HeaderConstructor:
    @classmethod
    def create(cls, method: str, **kwargs: Any) -> Header:
        if method == "binary file":
            return BinaryHeaderReader.header_from_file(kwargs["file"])
        else:
            raise ImportError
