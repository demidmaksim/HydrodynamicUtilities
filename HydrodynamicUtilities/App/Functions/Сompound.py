from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from HydrodynamicUtilities.App.GUI.UiMainWindow import Ui_MainWindow

from pathlib import Path

from HydrodynamicUtilities.Writer import get_pattern
from .SCHButtons import ScheduleCreatorApp
# from .ExcelButtons import AsciiReaderApp
from .HistButtons import HistCreatorApp


class TestClass(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def add_excel_to_sch(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getOpenFileNames()

            for r in results[0]:
                if r != "" and r != "All Files (*)":
                    wi = QtWidgets.QListWidgetItem(r)
                    # self.ui.WidgetItems.append(wi)
                    self.ui.listWidget_to_sch.addItem(wi)
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def add_sch_to_excel(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getOpenFileNames()

            for r in results[0]:
                if r != "" and r != "All Files (*)":
                    wi = QtWidgets.QListWidgetItem(r)
                    # self.ui.WidgetItems.append(wi)
                    self.ui.listWidget_to_excel_from_sch.addItem(wi)
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def add_hist(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getOpenFileNames()

            for r in results[0]:
                if r != "" and r != "All Files (*)":
                    wi = QtWidgets.QListWidgetItem(r)
                    # self.ui.WidgetItems.append(wi)
                    self.ui.listWidget_hist.addItem(wi)
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def del_excel_to_sch(self) -> None:
        try:
            for_del = []
            for wid in range(self.ui.listWidget_to_sch.count()):
                widget = self.ui.listWidget_to_sch.item(wid)
                if widget.isSelected():
                    for_del.append(self.ui.listWidget_to_sch.row(widget))

            for row in for_del[::-1]:
                self.ui.listWidget_to_sch.takeItem(row)

        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def del_sch_to_excel(self) -> None:
        try:
            for_del = []
            for wid in range(self.ui.listWidget_to_excel_from_sch.count()):
                widget = self.ui.listWidget_to_excel_from_sch.item(wid)
                if widget.isSelected():
                    value = self.ui.listWidget_to_excel_from_sch.row(widget)
                    for_del.append(value)

            for row in for_del[::-1]:
                self.ui.listWidget_to_excel_from_sch.takeItem(row)

        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def del_hist(self) -> None:
        try:
            for_del = []
            for wid in range(self.ui.listWidget_hist.count()):
                widget = self.ui.listWidget_hist.item(wid)
                if widget.isSelected():
                    value = self.ui.listWidget_hist.row(widget)
                    for_del.append(value)

            for row in for_del[::-1]:
                self.ui.listWidget_hist.takeItem(row)

        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def choose_target_folder_to_sch(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getExistingDirectory()
            if results != "":
                self.ui.lineEdit_target_folder_to_sch.setText(results)
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def choose_target_folder_to_excel(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getExistingDirectory()
            if results != "":
                self.ui.lineEdit_target_folder_to_excel.setText(results)
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def choose_target_folder_hist(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getExistingDirectory()
            if results != "":
                self.ui.lineEdit_target_folder_hist.setText(results)
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def scheck_excel_to_sch(self) -> None:
        try:
            ScheduleCreatorApp().data_validate(self.ui)
        except BaseException:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def screate_sch_from_excel(self) -> None:
        creator = ScheduleCreatorApp()
        creator.create_schedule(self.ui)

    def create_excel_pattern_sch(self) -> None:
        try:
            win = QtWidgets.QFileDialog()

            results = win.getSaveFileName(filter="*.xlsx")
            if results[0] != "":
                get_pattern(Path(results[0]))
        except:
            text = "Error! Не предвиденная ошибка"
            self.ui.textBrowser_log.append(text)
            return None

    def create_excel_from_sch(self) -> None:
        # creator = AsciiReaderApp()
        # creator.create_excel(self.ui)
        pass

    def check_hist_files(self) -> None:
        pass

    def create_from_hist_files(self) -> None:
        HistCreatorApp().create(self.ui)

    def create_hist_pattern(self) -> None:
        pass
