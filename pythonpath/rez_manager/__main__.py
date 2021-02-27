import sys

from Qt import QtWidgets

from .gui import ManagerWin


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ManagerWin()
    win.show()
    sys.exit(app.exec_())
