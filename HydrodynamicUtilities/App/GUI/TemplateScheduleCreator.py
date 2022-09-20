from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List
    from HydrodynamicModelAnalysis.Models.ExcelFile import RawExcelDataDict

import os

from PySide6 import QtCore, QtWidgets
from pathlib import Path

from Writer import get_pattern, create_schedule
from HydrodynamicModelAnalysis.Models import TimeVector, generate_time_vector, TimePoint
from Reader.ExcelReader import BaseReader
from HydrodynamicModelAnalysis.Models.Strategy.Frame import ScheduleDataframe
from HydrodynamicModelAnalysis.Models.Strategy.Validator import Validator


class APPScheduleValidator(Validator):
    log_method = None

    @classmethod
    def log(cls, string: str, log_type: str) -> None:
        cls.log_method.append(string)


class HistoryChoiceWidget(QtWidgets.QWidget):
    def __init__(self, form) -> None:

        # pyqt6-tool / designer / .ui

        super().__init__()
        # form.setObjectName("Form")
        # form.resize(1114, 759)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(form)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.splitter = QtWidgets.QSplitter(form)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.BottomAddedFile = QtWidgets.QPushButton(self.layoutWidget)
        self.BottomAddedFile.setObjectName("BottomAddedFile")
        self.gridLayout_2.addWidget(self.BottomAddedFile, 0, 0, 1, 1)
        self.LabelFinish = QtWidgets.QLabel(self.layoutWidget)
        self.LabelFinish.setObjectName("LabelFinish")
        self.gridLayout_2.addWidget(self.LabelFinish, 3, 0, 1, 1)
        self.DateEditStart = QtWidgets.QDateEdit(self.layoutWidget)
        self.DateEditStart.setWrapping(False)
        self.DateEditStart.setFrame(True)
        self.DateEditStart.setAccelerated(False)
        self.DateEditStart.setKeyboardTracking(True)
        self.DateEditStart.setProperty("showGroupSeparator", True)
        self.DateEditStart.setDateTime(
            QtCore.QDateTime(QtCore.QDate(2022, 5, 2), QtCore.QTime(0, 0, 0))
        )
        self.DateEditStart.setCurrentSection(QtWidgets.QDateTimeEdit.Section.DaySection)
        self.DateEditStart.setCalendarPopup(False)
        self.DateEditStart.setObjectName("DateEditStart")
        self.gridLayout_2.addWidget(self.DateEditStart, 1, 1, 1, 1)
        self.BottomCheckFiles = QtWidgets.QPushButton(self.layoutWidget)
        self.BottomCheckFiles.setObjectName("BottomCheckFiles")
        self.gridLayout_2.addWidget(self.BottomCheckFiles, 0, 2, 1, 1)
        self.CheckBoxInToOneFile = QtWidgets.QCheckBox(self.layoutWidget)
        self.CheckBoxInToOneFile.setText("")
        self.CheckBoxInToOneFile.setObjectName("CheckBoxInToOneFile")
        self.gridLayout_2.addWidget(self.CheckBoxInToOneFile, 3, 3, 1, 1)
        self.LabelStart = QtWidgets.QLabel(self.layoutWidget)
        self.LabelStart.setObjectName("LabelStart")
        self.gridLayout_2.addWidget(self.LabelStart, 1, 0, 1, 1)
        self.DateEditFinish = QtWidgets.QDateEdit(self.layoutWidget)
        self.DateEditFinish.setDateTime(
            QtCore.QDateTime(QtCore.QDate(2173, 1, 2), QtCore.QTime(0, 0, 0))
        )
        self.DateEditFinish.setObjectName("DateEditFinish")
        self.gridLayout_2.addWidget(self.DateEditFinish, 3, 1, 1, 1)
        self.BottomCreateSchedule = QtWidgets.QPushButton(self.layoutWidget)
        self.BottomCreateSchedule.setObjectName("BottomCreateSchedule")
        self.gridLayout_2.addWidget(self.BottomCreateSchedule, 0, 3, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.spinBox.setMinimum(1)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_2.addWidget(self.spinBox)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 4, 1, 1)
        self.LabelTimeStep = QtWidgets.QLabel(self.layoutWidget)
        self.LabelTimeStep.setObjectName("LabelTimeStep")
        self.gridLayout_2.addWidget(self.LabelTimeStep, 1, 2, 1, 1)
        self.BottomDeliteFile = QtWidgets.QPushButton(self.layoutWidget)
        self.BottomDeliteFile.setObjectName("BottomDeliteFile")
        self.gridLayout_2.addWidget(self.BottomDeliteFile, 0, 1, 1, 1)
        self.TimeStepChoice = QtWidgets.QComboBox(self.layoutWidget)
        self.TimeStepChoice.setObjectName("TimeStepChoice")
        self.gridLayout_2.addWidget(self.TimeStepChoice, 1, 3, 1, 1)
        self.BottomPatternCreate = QtWidgets.QPushButton(self.layoutWidget)
        self.BottomPatternCreate.setObjectName("BottomPatternCreate")
        self.gridLayout_2.addWidget(self.BottomPatternCreate, 0, 4, 1, 1)
        self.LabelInToOneFile = QtWidgets.QLabel(self.layoutWidget)
        self.LabelInToOneFile.setObjectName("LabelInToOneFile")
        self.gridLayout_2.addWidget(self.LabelInToOneFile, 3, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelTargetFolder = QtWidgets.QLabel(self.layoutWidget)
        self.labelTargetFolder.setObjectName("labelTargetFolder")
        self.horizontalLayout.addWidget(self.labelTargetFolder)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.ButtonChooseLoad = QtWidgets.QPushButton(self.layoutWidget)
        self.ButtonChooseLoad.setObjectName("ButtonChooseLoad")
        self.horizontalLayout.addWidget(self.ButtonChooseLoad)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(self.layoutWidget)
        self.listWidget.setMovement(QtWidgets.QListView.Movement.Free)
        self.listWidget.setLayoutMode(QtWidgets.QListView.LayoutMode.Batched)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.textBrowser = QtWidgets.QTextBrowser(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setMinimumSize(QtCore.QSize(300, 10))
        self.textBrowser.setSizeIncrement(QtCore.QSize(1000, 0))
        self.textBrowser.setBaseSize(QtCore.QSize(2000, 0))
        self.textBrowser.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout_3.addWidget(self.splitter)

        self.retranslate_ui(form)
        QtCore.QMetaObject.connectSlotsByName(form)
        # MY part

        self.BottomAddedFile.clicked.connect(self.adding_button)
        self.BottomDeliteFile.clicked.connect(self.del_button)
        self.BottomCreateSchedule.clicked.connect(self.create_schedule)
        self.BottomPatternCreate.clicked.connect(self.create_pattern)
        self.ButtonChooseLoad.clicked.connect(self.choice_target_folder)
        self.BottomCheckFiles.clicked.connect(self.check_files)

        self.WidgetItems = []

        self.listWidget.setLayoutMode(QtWidgets.QListView.LayoutMode.Batched)
        selection = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        self.listWidget.setSelectionMode(selection)

        form.setWindowTitle("ScheduleCreator")

        self.TimeStepChoice.addItems(["Месяц", "Год", "День"])

    def retranslate_ui(self, form):
        _translate = QtCore.QCoreApplication.translate
        form.setWindowTitle(_translate("Form", "Form"))
        self.BottomAddedFile.setText(_translate("Form", "Добавить"))
        self.LabelFinish.setText(_translate("Form", "Финиш"))
        self.BottomCheckFiles.setText(_translate("Form", "Проверить"))
        self.LabelStart.setText(_translate("Form", "Старт"))
        self.BottomCreateSchedule.setText(_translate("Form", "Собрать"))
        self.label.setText(_translate("Form", "Размер"))
        self.LabelTimeStep.setText(_translate("Form", "Временной шаг"))
        self.BottomDeliteFile.setText(_translate("Form", "Удалить"))
        self.BottomPatternCreate.setText(_translate("Form", "Создать Шаблон"))
        self.LabelInToOneFile.setText(_translate("Form", "В один файл"))
        self.labelTargetFolder.setText(_translate("Form", "Целевая папка"))
        self.ButtonChooseLoad.setText(_translate("Form", "Выбрать"))

    def del_button(self) -> None:
        try:
            for_del = []
            for widget in self.WidgetItems:
                if widget.isSelected():
                    for_del.append(self.listWidget.row(widget))

            for row in for_del[::-1]:
                self.listWidget.takeItem(row)
                # self.WidgetItems.remove(row)
        except:
            text = "Error! Не предвиденная ошибка"
            self.textBrowser.append(text)
            return None

    def adding_button(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getOpenFileNames()

            for r in results[0]:
                if r != "" and r != "All Files (*)":
                    wi = QtWidgets.QListWidgetItem(r)
                    self.WidgetItems.append(wi)
                    self.listWidget.addItem(wi)
        except:
            text = "Error! Не предвиденная ошибка"
            self.textBrowser.append(text)
            return None

    def create_pattern(self) -> None:
        try:
            win = QtWidgets.QFileDialog()

            results = win.getSaveFileName(filter="*.xlsx")
            if results[0] != "":
                get_pattern(Path(results[0]))
        except:
            text = "Error! Не предвиденная ошибка"
            self.textBrowser.append(text)
            return None

    def choice_target_folder(self) -> None:
        try:
            win = QtWidgets.QFileDialog()
            results = win.getExistingDirectory()
            if results != "":
                self.lineEdit.setText(results)
        except:
            text = "Error! Не предвиденная ошибка"
            self.textBrowser.append(text)
            return None

    def __get_time_vector(self) -> Optional[TimeVector]:
        sta = TimePoint(self.DateEditStart.dateTime().toString("yyyy-MM-dd"))
        fin = TimePoint(self.DateEditFinish.dateTime().toString("yyyy-MM-dd"))
        value_step = self.spinBox.value()

        if sta == fin:
            text = "Warning! Дата старта совпадвет с датой финиша"
            self.textBrowser.append(text)
            return None

        if self.TimeStepChoice.currentText() == "Месяц":
            step = "M"
        elif self.TimeStepChoice.currentText() == "Год":
            step = "Y"
        elif self.TimeStepChoice.currentText() == "День":
            step = "D"
        else:
            return None

        return generate_time_vector(sta, fin, step, value_step)

    def __get_list(self) -> List[Path]:
        strategy_list = []

        for row in range(self.listWidget.count()):
            widget = self.listWidget.item(row)
            strategy_list.append(Path(widget.text()))

        if not strategy_list:
            text = "Warning! Не выбраны файлы"
            self.textBrowser.append(text)

        return strategy_list

    def __get_directory(self) -> Path:
        if self.lineEdit.text() == "":
            return Path(os.path.abspath(os.curdir))
        else:
            return Path(self.lineEdit.text())

    def __create_each_separately(
        self, time_vector: TimeVector, redd: RawExcelDataDict, target_dir: Path
    ) -> None:
        for ref in redd:
            sdf = ref.get_schedule_dataframe()
            source_link = target_dir / (ref.get_name() + ".sch")
            create_schedule(sdf, time_vector, source_link)
            target_folder = Path(self.lineEdit.text())
            target_link = target_folder / (ref.get_name() + ".sch")
            text = f"Completed!\t" f"File {target_link} Created!"
            self.textBrowser.append(text)

    def __create_jointly(
        self, time_vector: TimeVector, redd: RawExcelDataDict, target_dir: Path
    ) -> None:
        sdf = ScheduleDataframe()
        for ref in redd:
            new_sdf = ref.get_schedule_dataframe()
            sdf = sdf + new_sdf

        ref = redd[list(redd.Data.keys())[0]]
        source_link = target_dir / (ref.get_name() + ".sch")
        create_schedule(sdf, time_vector, source_link)
        target_folder = Path(self.lineEdit.text())
        target_link = target_folder / (ref.get_name() + ".sch")
        text = f"Completed!\t" f"File {target_link} Created!"
        self.textBrowser.append(text)

    def create_schedule(self) -> None:
        try:
            time_vector = self.__get_time_vector()
            path_list = self.__get_list()
            target_dir = self.__get_directory()

            if time_vector is None:
                return None

            if not path_list:
                return None

            redd = BaseReader.read_excel_files(path_list)
            if self.CheckBoxInToOneFile.isChecked():
                self.__create_jointly(time_vector, redd, target_dir)
            else:
                self.__create_each_separately(time_vector, redd, target_dir)

        except BaseException:
            text = "Error! Не предвиденная ошибка"
            self.textBrowser.append(text)
            return None

    def check_files(self) -> None:
        try:
            path_list = self.__get_list()
            APPScheduleValidator.log_method = self.textBrowser
            redd = BaseReader.read_excel_files(path_list)
            APPScheduleValidator.check(redd)

        except BaseException:
            text = "Error! Не предвиденная ошибка"
            self.textBrowser.append(text)
            return None
