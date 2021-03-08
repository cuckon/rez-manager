import os
from functools import partial

from Qt import QtWidgets, QtGui

from .models import RezPackagesModel
from .views import SpreadsheetView


class ManagerWin(QtWidgets.QMainWindow):
    """Main window class."""
    def __init__(self):
        super(ManagerWin, self).__init__()
        self.setup_ui()

        self.spreadsheet = self.setup_spreadsheet()
        self.centralWidget().layout().addWidget(self.spreadsheet)

        self._connect()

        self.spreadsheet.model().reload()

    def _connect(self):
        slot_reload = self.spreadsheet.model().reload
        self.spreadsheet.packageDeleted.connect(
            partial(self.show_status_message, 'Deleted.')
        )
        self.spreadsheet.packageLocalised.connect(
            partial(self.show_status_message, 'Localised.')
        )
        self.spreadsheet.packageDeleted.connect(slot_reload)
        self.spreadsheet.packageLocalised.connect(slot_reload)


    def setup_ui(self):
        """Do the general ui setup work."""

        # Layout
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QVBoxLayout())
        self.setCentralWidget(central_widget)

        # Statusbar
        statusbar = QtWidgets.QStatusBar()
        self.setStatusBar(statusbar)

        # Appearance
        version = os.environ['REZ_MANAGER_VERSION']
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
