from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from HydrodynamicUtilities.App.GUI.UiMainWindow import Ui_MainWindow

import os

from pathlib import Path


from HydrodynamicUtilities.Models.Strategy.Frame import ScheduleDataframe
from HydrodynamicUtilities.Reader.ReaderASCII import read_schedule_section
from HydrodynamicUtilities.Writer.Schedule.ToExcel import write_xlsx


class AsciiReaderApp:
    def __get_list(self, ui: Ui_MainWindow) -> List[Path]:
        strategy_list = []

        for row in range(ui.listWidget_to_excel_from_sch.count()):
            widget = ui.listWidget_to_excel_from_sch.item(row)
            strategy_list.append(Path(widget.text()))

        if not strategy_list:
            text = "Warning! Не выбраны файлы"
            ui.textBrowser_log.append(text)

        return strategy_list

    def __get_directory(self, ui: Ui_MainWindow) -> Path:
        if ui.lineEdit_target_folder_to_excel.text() == "":
            return Path(os.path.abspath(os.curdir))
        else:
            return Path(ui.lineEdit_target_folder_to_excel.text())

    def __create_each_separately(
        self, ui: Ui_MainWindow, path_list: List[Path], target_path: Path
    ) -> None:
        for path in path_list:
            data = read_schedule_section(path)
            sdf = data.SCHEDULE.Sdf
            filename, file_extension = os.path.splitext(path.name)
            write_xlsx(sdf, target_path / f"{filename}.xlsx")
            text = f"Completed!\t" f"File {target_path}/{filename}/.xlsx Created!"
            ui.textBrowser_log.append(text)

    def __create_jointly(
        self, ui: Ui_MainWindow, path_list: List[Path], target_path: Path
    ) -> None:
        all_sdf = ScheduleDataframe()
        for path in path_list:
            data = read_schedule_section(path)
            sdf = data.SCHEDULE.Sdf
            all_sdf = all_sdf + sdf

        filename, file_extension = os.path.splitext(path_list[0].name)
        write_xlsx(all_sdf, target_path / f"{filename}.xlsx")
        text = f"Completed!\t" f"File {target_path}/{filename}.xlsx Created!"
        ui.textBrowser_log.append(text)

    def create_excel(self, ui: Ui_MainWindow) -> None:
        try:
            path_list = self.__get_list(ui)
            target_dir = self.__get_directory(ui)

            if not path_list:
                return None

            if ui.checkBox_in_one_file_sch.isChecked():
                self.__create_jointly(ui, path_list, target_dir)
            else:
                self.__create_each_separately(ui, path_list, target_dir)

        except BaseException:
            text = "Error! Не предвиденная ошибка"
            ui.textBrowser_log.append(text)
            return None
