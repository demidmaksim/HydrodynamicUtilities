from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List
    from HydrodynamicUtilities.Models.ExcelFile import RawExcelDataDict


from HydrodynamicUtilities.App.GUI.UiMainWindow import Ui_MainWindow

import os

from pathlib import Path

from HydrodynamicUtilities.Writer import create_schedule
from HydrodynamicUtilities.Models.Time import (
    TimeVector,
    generate_time_vector,
    TimePoint,
)
from HydrodynamicUtilities.Reader.ExcelReader import BaseReader
from HydrodynamicUtilities.Models.Strategy.Frame import ScheduleDataframe
from HydrodynamicUtilities.Models.Strategy.Validator import Validator


class APPScheduleValidator(Validator):
    log_method = None

    @classmethod
    def log(cls, string: str, log_type: str) -> None:
        cls.log_method.append(string)


class ScheduleCreatorApp:
    def __get_time_vector(self, ui: Ui_MainWindow) -> Optional[TimeVector]:
        sta = TimePoint(ui.dateEdit_start_date_to_sch.dateTime().toString("yyyy-MM-dd"))
        fin = TimePoint(ui.dateEdit_end_date_to_sch.dateTime().toString("yyyy-MM-dd"))
        value_step = ui.spinBox_size_to_sch.value()

        if sta == fin:
            text = "Warning! Дата старта совпадвет с датой финиша"
            ui.textBrowser_log.append(text)
            return None

        if ui.comboBox_choose_value_stepto_sch.currentText() == "Месяц":
            step = "M"
        elif ui.comboBox_choose_value_stepto_sch.currentText() == "Год":
            step = "Y"
        elif ui.comboBox_choose_value_stepto_sch.currentText() == "День":
            step = "D"
        elif ui.comboBox_choose_value_stepto_sch.currentText() == "Час":
            step = "h"
        else:
            return None

        return generate_time_vector(sta, fin, step, value_step)

    def __get_list(self, ui: Ui_MainWindow) -> List[Path]:
        strategy_list = []

        for row in range(ui.listWidget_to_sch.count()):
            widget = ui.listWidget_to_sch.item(row)
            strategy_list.append(Path(widget.text()))

        if not strategy_list:
            text = "Warning! Не выбраны файлы"
            ui.textBrowser_log.append(text)

        return strategy_list

    def __get_directory(self, ui: Ui_MainWindow) -> Path:
        if ui.lineEdit_target_folder_to_sch.text() == "":
            return Path(os.path.abspath(os.curdir))
        else:
            return Path(ui.lineEdit_target_folder_to_sch.text())

    def __create_each_separately(
        self,
        ui: Ui_MainWindow,
        time_vector: TimeVector,
        redd: RawExcelDataDict,
        target_dir: Path,
    ) -> None:
        for ref in redd:
            sdf = ref.get_schedule_dataframe()
            source_link = target_dir / (ref.get_name() + ".sch")
            create_schedule(sdf, time_vector, source_link)
            target_folder = Path(ui.lineEdit_target_folder_to_sch.text())
            target_link = target_folder / (ref.get_name() + ".sch")
            text = f"Completed!\t" f"File {target_link} Created!"
            ui.textBrowser_log.append(text)

    def __create_jointly(
        self,
        ui: Ui_MainWindow,
        time_vector: TimeVector,
        redd: RawExcelDataDict,
        target_dir: Path,
    ) -> None:
        sdf = ScheduleDataframe()
        for ref in redd:
            new_sdf = ref.get_schedule_dataframe()
            sdf = sdf + new_sdf

        ref = redd[list(redd.Data.keys())[0]]
        source_link = target_dir / (ref.get_name() + ".sch")
        create_schedule(sdf, time_vector, source_link)
        target_folder = Path(ui.lineEdit_target_folder_to_sch.text())
        target_link = target_folder / (ref.get_name() + ".sch")
        text = f"Completed!\t" f"File {target_link} Created!"
        ui.textBrowser_log.append(text)

    def create_schedule(self, ui: Ui_MainWindow) -> None:
        try:
            time_vector = self.__get_time_vector(ui)
            path_list = self.__get_list(ui)
            target_dir = self.__get_directory(ui)

            if time_vector is None:
                return None

            if not path_list:
                return None

            redd = BaseReader.read_excel_files(path_list)
            if ui.checkBox_in_one_file_to_sch.isChecked():
                self.__create_jointly(ui, time_vector, redd, target_dir)
            else:
                self.__create_each_separately(ui, time_vector, redd, target_dir)

        except BaseException:
            text = "Error! Не предвиденная ошибка"
            ui.textBrowser_log.append(text)
            return None

    def data_validate(self, ui: Ui_MainWindow) -> None:
        path_list = self.__get_list(ui)
        APPScheduleValidator.log_method = ui.textBrowser_log
        redd = BaseReader.read_excel_files(path_list)
        APPScheduleValidator.check(redd)
