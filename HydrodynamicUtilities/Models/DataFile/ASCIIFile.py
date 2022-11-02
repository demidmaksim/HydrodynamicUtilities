from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple

import numpy as np
import re
from ..Source.EtNKW_crutch import data as all_keyword



class ASCIIRow:
    def __init__(self, data: str) -> None:
        self.__data = data

    def __str__(self) -> str:
        return self.__data

    def strip_slash(self) -> ASCIIRow:
        # TODO
        data = self.__data
        return ASCIIRow(data)


class ASCIIText:
    def __init__(self, text: str) -> None:
        text = re.subn(r"--.*\n", "\n", text, flags=re.ASCII)[0]
        # TODO check \.
        text = re.subn(r"/\s*\n", "/\n", text, flags=re.ASCII)[0]

        text = text.strip()
        self.Text = text

    def __repr__(self) -> str:
        return self.Text[:100]

    def __str__(self) -> str:
        return self.Text

    def empty(self) -> bool:
        if self.Text == "":
            return True
        else:
            return False

    def __get_first_word(self) -> Tuple[int, int, str]:
        find_iter = re.finditer(r"\s*[a-zA-Z]\w*\s*", self.Text, flags=re.ASCII)
        find = find_iter.__next__()
        start = find.regs[0][0]
        end = find.regs[0][1]
        return start, end, self.Text[start:end].strip()

    def get_keyword(self, pop: bool = False) -> ASCIIRow:
        # TODO
        start, end, fw = self.__get_first_word()

        if fw in all_keyword:
            kw = fw
        elif fw[:3] == "ARR":
            kw = fw
        elif fw[:8] in all_keyword:
            kw = fw
        else:
            raise ValueError

        if pop:
            self.Text = self.Text[end:].strip()

        return ASCIIRow(kw)

    def get_first_word(self, pop: bool = False) -> ASCIIRow:
        values = []

        try:
            values.append(self.Text.index("\n"))
        except ValueError:
            pass

        try:
            values.append(self.Text.index("\t"))
        except ValueError:
            pass

        try:
            values.append(self.Text.index(" "))
        except ValueError:
            pass

        if values:
            min_ind = min(values)
        else:
            min_ind = -2

        results = self.Text[:min_ind]

        if pop:
            self.Text = self.Text[min_ind:]

        return ASCIIRow(results)

    def check_multiplication(self) -> bool:
        if "*" in self.Text:
            return True
        else:
            return False

    def replace_multiplication(self) -> ASCIIText:
        if not self.check_multiplication():
            return ASCIIText(self.Text)

        results = []
        for word in self.Text.split():
            if "*" in word:
                try:
                    value = word.split("*")[1]
                    if value == "":
                        value = "1*"
                    amount = int(word.split("*")[0])
                    reiteration = [value] * amount
                except IndexError:
                    amount = int(word.split("*")[0])
                    reiteration = ["1*"] * amount
                except ValueError:
                    reiteration = [word]
                results.extend(reiteration)

            else:
                results.append(word)

        return ASCIIText(" ".join(results))

    def get_cub(self) -> np.ndarray:
        text = self.to_slash()

        if not text.check_multiplication():
            list_results = text.split()
            return np.array(list_results, dtype=float)

        results = []

        target_text = re.subn(r"\n", " ", str(text), flags=re.ASCII)[0]
        target_text = re.subn(r"\t", " ", target_text, flags=re.ASCII)[0]

        start_block = 0
        find = re.finditer(r"\*", target_text, flags=re.ASCII)

        for string in find:
            pass
            ind = string.regs[0][0]
            left_ind = target_text.rfind(" ", start_block, ind)
            if left_ind == -1:
                left_ind = 0

            right_ind = target_text.find(" ", ind)
            mylt = target_text[left_ind:right_ind].strip().split("*")
            data = int(mylt[0]) * f" {mylt[1]}"
            results.append(target_text[start_block:left_ind])
            results.append(data)
            start_block = right_ind
        else:
            results.append(target_text[start_block:])

        string_results = " ".join(results)
        list_results = string_results.split()
        return np.array(list_results, dtype=float)

    def to_slash(self, pop: bool = False, end_slash: bool = False) -> ASCIIText:
        if end_slash:
            ind = self.Text.find("/\n")
        else:
            ind = self.Text.find("/")

        text = self.Text[: ind + 1]

        if pop:
            self.Text = self.Text[ind + 1 :].strip()

        return ASCIIText(text[:-1])

    def del_slash(self) -> ASCIIText:
        return ASCIIText(self.Text.replace("/", "").strip())

    def split(self) -> List[str]:
        return self.Text.split()
