from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Union

from pathlib import Path

from HydrodynamicModelAnalysis.Models.Source.EtNKW_crutch import data

# relative_path = "../../Models/Source/Eclipse_tNavigator.kwd"
# path = Path(os.path.abspath(__file__)).parent / relative_path
# all_ecl_keyword = pd.read_csv(path, header=None).iloc[:, 0].to_list()

all_ecl_keyword = data


class ASCIIRow:
    def __init__(self, text: str):
        self.Text = text

    def __repr__(self) -> str:
        return self.Text

    def __str__(self) -> str:
        return self.Text

    def __getitem__(self, item) -> ASCIIRow:
        return ASCIIRow(self.Text[item])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, object):
            return NotImplemented

        if isinstance(other, str):
            return self.Text == other
        elif isinstance(other, ASCIIFile):
            return self.Text == other.Text
        else:
            return False

    def upper(self) -> ASCIIRow:
        return ASCIIRow(self.Text.upper())

    def lower(self) -> ASCIIRow:
        return ASCIIRow(self.Text.lower())

    def chek_comment(self) -> bool:
        if "--" in self.Text:
            return True
        else:
            return False

    def chek_block(self) -> bool:
        if '"' in self.Text or "'" in self.Text:
            return True
        else:
            return False

    def chek_skip(self) -> bool:
        text = self.clean().Text
        if text.strip() == "":
            return True
        elif text.strip() == "/":
            return True
        else:
            return False

    def chek_multiplication(self) -> bool:
        if "*" in self.Text:
            return True
        else:
            return False

    def check_empty_slash(self) -> bool:
        return self.Text.strip() == "/"

    def check_keyword(self) -> bool:
        for kw in all_ecl_keyword:
            if kw in self.Text:
                return True
        return False

    def def_right_block(self) -> int:

        try:
            ind1 = self.Text.rindex("'")
        except ValueError:
            ind1 = -1

        try:
            ind2 = self.Text.rindex('"')
        except ValueError:
            ind2 = -1

        return max([ind1, ind2])

    def clean(self, slash_flag: bool = False) -> ASCIIRow:

        line = self.Text

        while "--" in line:
            ind_dash = line.index("--")
            try:
                ind_end = line.index("\n") + 1
            except ValueError:
                ind_end = len(line)
            line = line.replace(line[ind_dash:ind_end], "")

        if self.chek_block():
            ind = self.def_right_block()

            try:
                ind = line.index("/", ind)
                line = line[0 : ind + 1]
            except ValueError:
                pass

        if slash_flag:
            try:
                ind = line.rindex("/")
                line = line[0:ind]
            except ValueError:
                pass

        line = line.strip()

        return ASCIIRow(line)

    def clean_slash(self) -> ASCIIRow:
        try:
            ind = self.Text.rindex("/")
            line = self.Text[0:ind]
        except ValueError:
            return self

        line = line.strip()

        return ASCIIRow(line)

    def del_symbols(self, string: str) -> ASCIIRow:
        new = self.Text
        while string in new:
            new = new.replace(string, "")
        return ASCIIRow(new)

    def get_first_word(
        self, letter_case: str = "upper", length: int = None
    ) -> Optional[str]:
        try:
            word = self.Text.strip().split()[0]

            if length is not None:
                return word[:length]

            if letter_case is None:
                return word
            elif letter_case == "upper":
                return word.upper()
            elif letter_case == "lower":
                return word.lower()

        except IndexError:
            return None

    def split(self) -> List[str]:
        return self.Text.split()

    def split_not_mask(self) -> List[str]:
        t = self.Text
        t = t.replace('"', "'")
        list_t = t.split("'")
        results = []
        for vid, value in enumerate(list_t):
            if (vid + 1) % 2 == 1:
                results.extend(value.split())
            else:
                results.append(f"'{value}'")
        return results

    @property
    def replace_multiplication(self) -> ASCIIRow:
        if not self.chek_multiplication():
            return ASCIIRow(self.Text)

        results = []
        for word in self.Text.split():
            if ASCIIRow(word).chek_multiplication():
                try:
                    value = word.split("*")[1]
                    if value == "":
                        value = "1*"
                    amount = int(word.split("*")[0])
                    repetition = [value] * amount
                except IndexError:
                    amount = int(word.split("*")[0])
                    repetition = ["1*"] * amount
                except ValueError:
                    repetition = [word]
                results.extend(repetition)

            else:
                results.append(word)

        return ASCIIRow(" ".join(results))

    def empty(self) -> bool:
        return self.Text.strip() == ""

    def get_path(self) -> Path:

        if "'" in self.Text:
            target_latter = "'"
        elif '"' in self.Text:
            target_latter = '"'
        else:
            target_latter = None

        if target_latter is None:
            return Path(self.Text.split()[1])
        else:
            source = self.Text.split()[1]
            ind_f = source.index(target_latter)
            ind_s = source.index(target_latter, ind_f + 1)
            return Path(source[ind_f + 1 : ind_s])


class ASCIIFile:
    def __init__(self, text: str, path: Path) -> None:
        self.Text = text
        self.Path = path

    def append(self, other: ASCIIFile, index: int = 0) -> None:
        f_text: str = self.Text[:index]
        s_text: str = self.Text[index + 1 :]
        self.Text = "\n".join([f_text, "\n", other.Text, "\n", s_text])

    def read_string(self, predict=False) -> ASCIIRow:
        ind = self.Text.index("\n")
        if predict:
            return ASCIIRow(self.Text[:ind])
        else:
            lene = self.Text[:ind]
            self.Text = self.Text[ind + 1 :]
            return ASCIIRow(lene)

    def find_first_keyword(self) -> int:
        i = None
        for kw in all_ecl_keyword:
            if kw in all_ecl_keyword:
                ind = self.Text.index(kw)
                if i is None:
                    i = ind
                elif i > ind:
                    i = ind
        if i is None:
            return 0
        else:
            return i

    def read_to_slash(self, predict=False, replace_n=True) -> ASCIIRow:
        init_ind = 0
        ind = self.Text.index("/")
        row = ASCIIRow(self.Text[init_ind : ind + 1])
        row = row.clean()

        while row.empty():
            init_ind = ind
            ind = self.Text.index("/", ind + 1)
            row = ASCIIRow(self.Text[init_ind + 1 : ind])
            row = row.clean()

        if not predict:
            self.Text = self.Text[ind + 1 :]

        if replace_n:
            row.del_symbols("\n")

        return row

    def read_to_double_slas(self, predict=False, replace_n=True) -> List[ASCIIRow]:
        results = list()
        lines = self.Text.split("\n")
        for line in lines:
            aline = ASCIIRow(line)
            if aline.check_keyword():
                self.Text = "\n".join(lines)
                break
            elif aline.check_keyword():
                pass

    def read_aritmetic(self) -> List[str]:
        predict = self.read_string(predict=True)
        results = []
        while predict.clean() != "/":
            if predict.chek_skip():
                pass
            elif (
                "=" not in predict.Text and predict.get_first_word() in all_ecl_keyword
            ):
                break
            line = self.read_string()
            results.append(line.Text)
            predict = self.read_string(predict=True)

        return results

    def read_path(
        self,
        predict=False,
    ) -> ASCIIRow:
        i = 0
        one_apostrophe = False
        two_apostrophe = False
        while i < len(self.Text):
            latter = self.Text[i]

            if latter == "'" and one_apostrophe:
                one_apostrophe = False
            elif latter == "'" and not one_apostrophe:
                one_apostrophe = True

            if latter == '"' and two_apostrophe:
                two_apostrophe = False
            elif latter == '"' and not two_apostrophe:
                two_apostrophe = True

            if latter == "/" and not one_apostrophe and not two_apostrophe:
                break

            i += 1

        row = ASCIIRow(self.Text[:i])
        row = row.clean()

        if not predict:
            self.Text = self.Text[i + 1 :]

        return row

    def read_row(self) -> ASCIIRow:
        predict = self.read_to_slash(replace_n=True)
        predict = predict.clean()
        predict = predict.replace_multiplication
        return predict

    @property
    def not_end(self) -> bool:
        return self.Text != ""
