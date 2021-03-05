import os
import shutil
from functools import partial

import qtawesome as qta
from Qt import QtWidgets, QtGui, QtCore
from rez import packages
from rez.config import config
from rez.package_repository import package_repository_manager


def generate_tooltip(package):
    """Generate a proper tooltip for item"""
    tooltip = [package.format(
        '<h3>{name}</h3>'
        '{description}<br>'
        'Is Local: {is_local}<br>'
    )]
    if package.tools:
        tooltip.append('Tools: ' + ', '.join(package.tools))

    return '<br>'.join(tooltip)


def get_local_repo_index():
    packages_path = config.get('packages_path', [])
    local_packages_path = config.get('local_packages_path')
    if local_packages_path in packages_path:
        return packages_path.index(local_packages_path)
    return -1


def delete_local(packages, all_version: bool):
    for package in packages:
        package_dir = os.path.join(package.resource.location, package.name)

        if all_version:
            shutil.rmtree(package_dir)
        else:
            version_dir = os.path.join(package_dir, str(package.version))
            shutil.rmtree(version_dir)


class SpreadsheetView(QtWidgets.QTreeView):
    itemDeleted = QtCore.Signal()

    def __init__(self, parent=None):
        super(SpreadsheetView, self).__init__(parent)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.ExtendedSelection)

    # def selectedItem(self):
    #     indexes = self.selectionModel().selectedIndexes()
    #     for i in indexes:
    #         print(i.row(), i.column())
    #     return indexes[0] if indexes else None

    def contextMenuEvent(self, event):
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            return

        menu = QtWidgets.QMenu(self)
        model = self.model()

        self._add_delete_local_menu(menu, indexes)
        self._add_one_package_menu(menu, indexes)

        menu.addAction(qta.icon('fa.refresh'), 'Update', model.reload)
        menu.exec(event.globalPos())

    def _add_one_package_menu(self, menu, indexes):
        if indexes and self.model().itemFromIndex(indexes[0]).text():
            menu.addAction(
                qta.icon('fa.folder'),
                'Open Folder',
                partial(self.open_folder, indexes[0])
            )

    def _add_delete_local_menu(self, menu, indexes):
        local_repo_table_index = get_local_repo_index() + 1
        to_delete = []
        model = self.model()

        for index in indexes:
            if index.column() == local_repo_table_index:
                item = model.itemFromIndex(index)
                version = item.text()
                if version:
                    to_delete.append(item.latest)

        if to_delete:
            menu.addAction(
                'Delete Local Package(All Versions)',
                partial(self.on_delete_local, to_delete, True)
            )
            menu.addAction(
                'Delete Local Package',
                partial(self.on_delete_local, to_delete, False)
            )

            menu.addSeparator()

    def on_delete_local(self, packages, all_version):
        delete_local(packages, all_version)
        self.itemDeleted.emit()

    def open_folder(self, index):
        item = self.model().itemFromIndex(index)
        if not item.latest:
            return
        folder = os.path.join(
            item.latest.resource.location,
            item.latest.name,
            str(item.latest.version),
        )
        os.startfile(folder)

class RezPackagesModel(QtGui.QStandardItemModel):

    def __init__(self, parent=None):
        self.repos = config.get('packages_path')
        super(RezPackagesModel, self).__init__(0, len(self.repos) + 1)
        self.setHorizontalHeaderLabels(['Package'] + self.repos)

    def reload(self):
        package_repository_manager.clear_caches()
        self.setRowCount(0)

        for fam in packages.iter_package_families():
            row = [QtGui.QStandardItem(fam.name)]
            versions = [None]
            version_max = None

            # Fill the spreadsheet
            for repo in self.repos:
                latest = packages.get_latest_package(fam.name, paths=[repo])
                if not latest:
                    row.append(QtGui.QStandardItem(''))
                    versions.append(None)
                else:
                    item = QtGui.QStandardItem(str(latest.version))
                    item.setToolTip(generate_tooltip(latest))
                    # item.setData(latest, QtCore.Qt.UserRole)
                    item.latest = latest
                    row.append(item)

                    version_max = max(latest.version, version_max) \
                        if version_max else latest.version
                    versions.append(latest.version or None)

            # Find the winner
            winner_found = False
            for i in range(len(self.repos)):
                if not winner_found and versions[i + 1] and versions[i + 1] == version_max:
                    winner_found = True
                else:
                    row[i + 1].setForeground(QtGui.QColor('gray'))

            self.appendRow(row)


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
        self.spreadsheet.itemDeleted.connect(self.on_deleted)

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

    def on_deleted(self):
        self.statusBar().showMessage('Deleted.', 4000)

    def setup_spreadsheet(self):
        view = SpreadsheetView()
        model = RezPackagesModel()
        view.setModel(model)
        return view
