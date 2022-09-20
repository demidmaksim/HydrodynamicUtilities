from PySide6 import QtWidgets

from App.Functions.Сompound import TestClass
from multiprocessing import freeze_support


if __name__ == "__main__":
    import sys

    # freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = TestClass()

    MainWindow.show()
    sys.exit(app.exec())
