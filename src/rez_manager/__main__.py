import sys

from Qt import QtWidgets

from .window import ManagerWin


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ManagerWin()
    win.resize(1200, 600)
    win.show()
    sys.exit(app.exec_())
