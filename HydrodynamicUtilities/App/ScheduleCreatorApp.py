from PySide6 import QtWidgets

from HydrodynamicUtilities.App.Functions.Сompound import TestClass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = TestClass()

    MainWindow.show()
    sys.exit(app.exec())
