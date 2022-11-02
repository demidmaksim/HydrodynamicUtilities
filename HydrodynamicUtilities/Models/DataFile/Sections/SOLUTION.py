from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Dict


from ..Base import Section, UnInitializedSection, Keyword


class SOLUTION(Section):
    __Keyword = {}

    FamousKeyword = tuple(__Keyword.keys())

    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return cls.__Keyword


class UnInitializedSOLUTION(UnInitializedSection):
    @classmethod
    def get_famous_keyword(cls) -> Dict[str, Type[Keyword]]:
        return SOLUTION.get_famous_keyword()
