import os
import logging
from functools import partial

from Qt import QtWidgets, QtGui

from .models import RezPackagesModel
from .views import SpreadsheetView
from .textedithandler import TextEditHandler


def _setup_logger(textedit):
    logger = logging.getLogger('rez_manager')
    log_handler = TextEditHandler(textedit)
    log_handler.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    return logger


class ManagerWin(QtWidgets.QMainWindow):
    """Main window class."""
    def __init__(self):
        super(ManagerWin, self).__init__()

        self.setup_window()

        self.splitter = QtWidgets.QSplitter(self.centralWidget())
        self.centralWidget().layout().addWidget(self.splitter)

        self.spreadsheet = self.setup_spreadsheet()
        self.splitter.addWidget(self.spreadsheet)

        self.log_widget = QtWidgets.QTextEdit()
        self.splitter.addWidget(self.log_widget)
        self.splitter.setSizes([800, 400])

        self.logger = _setup_logger(self.log_widget)

        self._connect()
        self.spreadsheet.model().reload()

    def _connect(self):
        slot_reload = self.spreadsheet.model().reload
        model = self.spreadsheet.model()

        self.spreadsheet.packageDeleted.connect(
            partial(self.show_status_message, 'Deleted.')
        )

        self.spreadsheet.packageDeleted.connect(slot_reload)
        model.packagesChanged.connect(slot_reload)

    def setup_window(self):
        """Do the general ui setup work."""
        # Layout
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QVBoxLayout())
        self.setCentralWidget(central_widget)

        # Statusbar
        statusbar = QtWidgets.QStatusBar()
        self.setStatusBar(statusbar)

        # Appearance
        version = os.environ['REZ_REZ_MANAGER_VERSION']
        self.setWindowTitle('Rez Packages Manager - ' + version)
        icon_path = os.path.join(
            os.environ['MANAGER_RESOURCES_FOLDER'], 'icon.png'
        )
        self.setWindowIcon(QtGui.QIcon(icon_path))

    def show_status_message(self, message):
        self.statusBar().showMessage(message, 4000)

    def setup_spreadsheet(self):
        view = SpreadsheetView()
        model = RezPackagesModel()
        # proxy_model = RezPackagesProxyModel()
        # proxy_model.setSourceModel(model)
        # view.setModel(proxy_model)
        view.setModel(model)
        return view
