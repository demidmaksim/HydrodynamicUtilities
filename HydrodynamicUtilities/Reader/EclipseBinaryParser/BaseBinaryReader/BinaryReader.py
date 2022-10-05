import os
from struct import unpack
from typing import Dict, BinaryIO, Iterator
from .Header import HeaderConstructor, Header
from .Content import Content
from pathlib import Path
import time


class RowBinaryData:
    def __init__(self) -> None:
        self.data: Dict[str, Content] = dict()

    def __getitem__(self, key: str) -> Content:
        value: Content = self.data[key]
        return value

    def __iter__(self) -> Iterator[Content]:
        for key in self.data:
            yield self.data[key]

    def append(self, content: Content) -> None:
        if content.keyword in self.data.keys():
            self.data[content.keyword].append(content.values[0])
        else:
            self.data[content.keyword] = content


class BinaryReader:
    determinant: int = 4  # 4 is size of zone(area) length determinant

    @classmethod
    def read_area(cls, file: BinaryIO, header: Header) -> bytes:

        read = 0
        bytes_list = []
        while read < header.length_block:
            size_area = unpack(">i", file.read(cls.determinant))[0]
            bytes_list.append(file.read(size_area))
            file.seek(cls.determinant, 1)
            read += size_area

        return b"".join(bytes_list)

    @classmethod
    def read_all_file(cls, link: Path) -> RowBinaryData:
        data = RowBinaryData()

        with open(link, "rb") as file:
            while file.tell() < os.path.getsize(link):
                header = HeaderConstructor.create("binary file", file=file)
                byte = cls.read_area(file, header)
                data.append(Content(header, byte))
        return data
