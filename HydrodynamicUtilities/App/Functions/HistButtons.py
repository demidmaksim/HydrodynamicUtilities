from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from HydrodynamicUtilities.App.GUI.UiMainWindow import Ui_MainWindow

import os

from pathlib import Path

from HydrodynamicUtilities.Writer import create_schedule
from HydrodynamicUtilities.Models.Time import TimePoint
from HydrodynamicUtilities.Reader.ExcelReader import BaseReader
from HydrodynamicUtilities.Models.Strategy.Frame import ScheduleDataframe
from HydrodynamicUtilities.Writer.Schedule.ToExcel import write_xlsx
from HydrodynamicUtilities.Models.HistoryData import FieldHistory


class HistCreatorApp:
    def __get_list(self, ui: Ui_MainWindow) -> List[Path]:
        strategy_list = []

        for row in range(ui.listWidget_hist.count()):
            widget = ui.listWidget_hist.item(row)
            strategy_list.append(Path(widget.text()))

        if not strategy_list:
            text = "Warning! Не выбраны файлы"
            ui.textBrowser_log.append(text)

        return strategy_list

    def __get_directory(self, ui: Ui_MainWindow) -> Path:
        if ui.lineEdit_target_folder_hist.text() == "":
            return Path(os.path.abspath(os.curdir))
        else:
            return Path(ui.lineEdit_target_folder_hist.text())

    @staticmethod
    def read_history_file(file_path: List[Path]) -> FieldHistory:
        data = BaseReader.read_excel_files(file_path, True)
        return data.get_field_history(
            other_event=True,
            read_construction_history=True,
        )

    @staticmethod
    def set_global_settings(ui: Ui_MainWindow, data: FieldHistory) -> None:
        sta = TimePoint(ui.dateEdit_start_date_hist.dateTime().toString("yyyy-MM-dd"))
        fin = TimePoint(ui.dateEdit_end_date_hist.dateTime().toString("yyyy-MM-dd"))

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

        value_step = ui.spinBox_size_to_sch.value()

        data.set_steps_settings(sta, fin, (step, value_step))

    @staticmethod
    def set_well_settings(ui: Ui_MainWindow, data: FieldHistory) -> None:
        stop_prod = ui.checkBox_prod_well_stop.isChecked()
        inje_stop = ui.checkBox_inj_well_stop.isChecked()
        wefac = ui.checkBox_wefac.isChecked()
        prod_control = ui.comboBox_hist_prod_control.currentText()
        inje_control = ui.comboBox_hist_inj_control.currentText()

        data.set_well_wefac_settings(wefac)
        data.set_well_prod_event_settings(stop_prod)
        data.set_well_prod_mode_settings(prod_control)
        data.set_well_inj_event_settings(inje_stop)
        data.set_well_inj_mode_settings(inje_control)

    def create_sdf(
        self,
        ui: Ui_MainWindow,
        field_history: FieldHistory,
    ) -> ScheduleDataframe:
        self.set_global_settings(ui, field_history)
        self.set_well_settings(ui, field_history)
        return field_history.get_all_events()

    def create_excel(
        self,
        ui: Ui_MainWindow,
        list_of_file_path: List[Path],
    ) -> None:
        fh = self.read_history_file(list_of_file_path)
        sdf = self.create_sdf(ui, fh)
        target = self.__get_directory(ui)
        name = fh.get_cipher()
        write_xlsx(sdf, target / f"{name}.xlsx")

    def create_sch(
        self,
        ui: Ui_MainWindow,
        list_of_file_path: List[Path],
    ) -> None:
        fh = self.read_history_file(list_of_file_path)
        sdf = self.create_sdf(ui, fh)
        target = self.__get_directory(ui)
        name = fh.get_cipher()
        create_schedule(sdf, fh.get_time_vector(), target / f"{name}.sch")

    def create(self, ui: Ui_MainWindow) -> None:
        one_file = ui.checkBox_in_one_file_sch.isChecked()
        to_excel = ui.checkBox_hist_to_excel.isChecked()
        list_of_file_path = self.__get_list(ui)

        if one_file and to_excel:
            self.create_excel(ui, list_of_file_path)
        elif one_file:
            self.create_sch(ui, list_of_file_path)
        else:
            for path in list_of_file_path:
                if to_excel:
                    self.create_excel(ui, [path])
                else:
                    self.create_sch(ui, [path])
