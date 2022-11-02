from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Dict


from ..Base import Section, UnInitializedSection, Keyword


class REGIONS(Section):
    __Keyword = {}

    __FamousKeyword = tuple(__Keyword.keys())

    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return cls.__Keyword


class UnInitializedREGIONS(UnInitializedSection):
    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return REGIONS.get_famous_keyword()
