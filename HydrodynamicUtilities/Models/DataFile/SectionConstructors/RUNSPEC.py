from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import DataFile

from copy import deepcopy

from HydrodynamicUtilities.Models.DataFile.Base import Keyword, UnknownKeyword
from HydrodynamicUtilities.Models.DataFile.ASCIIFile import ASCIIText
from HydrodynamicUtilities.Models.DataFile.Sections import RUNSPEC as RS
from HydrodynamicUtilities.Reader.ASCIIDataFileReader.BaseCreator import BaseKeywordCreator


class RunspecKeywordCreator(BaseKeywordCreator):
    @staticmethod
    def defines(data: ASCIIText) -> RS.DEFINES:
        results = RS.DEFINES()
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

            entry = RS.DEFINESEntry(
                results, name, value, min_value, max_value, var_type
            )
            results.append(entry)
        return results

    @staticmethod
    def tabdims(data: ASCIIText) -> RS.TABDIMS:
        data = data.replace_multiplication()
        sdata = data.to_slash()
        results = deepcopy(RS.TABDIMS.get_base_value())
        for pid, pos in enumerate(sdata.split()):
            kw = list(RS.TABDIMS.get_base_value().keys())[pid]
            results[kw] = pos
        return RS.TABDIMS(**results)

    @staticmethod
    def vapoil(*args) -> RS.VAPOIL:
        return RS.VAPOIL()

    @staticmethod
    def disgas(*args) -> RS.DISGAS:
        return RS.DISGAS()

    @staticmethod
    def water(*args) -> RS.WATER:
        return RS.WATER()

    @staticmethod
    def oil(*args) -> RS.OIL:
        return RS.OIL()

    @staticmethod
    def gas(*args) -> RS.GAS:
        return RS.GAS()

    @staticmethod
    def start(data: ASCIIText) -> RS.START:
        data = data.replace_multiplication()
        sdata = data.to_slash()
        results = deepcopy(RS.START.get_base_value())
        for pid, pos in enumerate(sdata.split()):
            kw = list(RS.START.get_base_value().keys())[pid]
            results[kw] = pos
        return RS.START(**results)

    @staticmethod
    def metric(*args) -> RS.METRIC:
        return RS.METRIC()

    @staticmethod
    def dimens(data: ASCIIText) -> RS.DIMENS:
        data = data.replace_multiplication()
        sdata = data.to_slash()
        results = deepcopy(RS.DIMENS.get_base_value())
        for pid, pos in enumerate(sdata.split()):
            kw = list(RS.DIMENS.get_base_value().keys())[pid]
            results[kw] = pos
        return RS.DIMENS(**results)

    def create(self, data: str, data_file: DataFile) -> Keyword:
        adata = ASCIIText(data)

        kw = adata.get_keyword(True)

        if str(kw) not in RS.RUNSPEC.get_famous_keyword().keys():
            return UnknownKeyword(str(kw), str(adata))

        fun = self.choose_fun(str(kw))
        return fun(adata)
