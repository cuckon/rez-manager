import os
import shutil
from functools import partial

import qtawesome as qta
from Qt import QtWidgets, QtGui, QtCore
from rez import packages
from rez.config import config
from rez.package_repository import package_repository_manager
from rez.package_copy import copy_package


def generate_item_tooltip(item):
    """Generate a proper tooltip for item"""
    latest = item.latest
    if not latest:
        return ''

    tooltip = []
    if item.empty_folder:
        tooltip.append('[Empty folder]')
    else:
        if latest.description:
            tooltip.append(latest.format('Description: {description}'))
        if latest.tools:
            tooltip.append('Tools: ' + ', '.join(latest.tools))

    return '\n'.join(tooltip)


def generate_item_text(item):
    if item.latest:
        return str(item.latest.version)

    if item.empty_folder:
        return '-'

    return ''


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
            children = os.listdir(package_dir)

            # Remove package folder instead of version folder to avoid leaving
            # empty folder
            if len(children) == 1:
                assert children[0] == str(package.version)
                to_delete = package_dir
            else:
                to_delete = os.path.join(package_dir, str(package.version))

            shutil.rmtree(to_delete)


class SpreadsheetView(QtWidgets.QTreeView):
    packageDeleted = QtCore.Signal()
    packageLocalised = QtCore.Signal()

    def __init__(self, parent=None):
        super(SpreadsheetView, self).__init__(parent)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.ExtendedSelection)

    def contextMenuEvent(self, event):
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            return

        menu = QtWidgets.QMenu(self)
        model = self.model()

        self._add_multiple_packages_menu(menu, indexes)
        self._add_one_package_menu(menu, indexes)

        menu.addAction(qta.icon('fa.refresh'), 'Update', model.reload)
        menu.exec(event.globalPos())

    def _add_one_package_menu(self, menu, indexes):
        if len(indexes) == 1 and indexes[0].column() != 0 and \
            self.model().itemFromIndex(indexes[0]).text():
            menu.addAction(
                qta.icon('fa.folder'),
                'Open Folder',
                partial(self.open_folder, indexes[0])
            )

    def _add_delete_packages_menu(
            self, indexes, model, local_repo_table_index, menu
    ):
        to_delete = []
        empty_package_folders = []

        for index in indexes:
            item = model.itemFromIndex(index)
            if index.column() == local_repo_table_index:
                if item.latest:
                    to_delete.append(item.latest)
                elif item.empty_folder:
                    empty_package_folders.append(item.empty_folder)

        actions = []
        if to_delete:
            actions.append(menu.addAction(
                'Delete Local Packages (All Versions)',
                partial(self.on_delete_local, to_delete, True)
            ))
            actions.append(menu.addAction(
                'Delete Local Packages',
                partial(self.on_delete_local, to_delete, False)
            ))

        if empty_package_folders:
            actions.append(menu.addAction(
                'Delete Empty Package Folder',
                partial(delete_empty_folder, empty_package_folders)
            ))

        return actions

    def _add_localise_package_menu(
            self, indexes, model, local_repo_table_index, menu
    ):
        to_localise = []

        for index in indexes:
            item = model.itemFromIndex(index)
            version = item.text()

            if index.column() not in [0, local_repo_table_index]:
                if version:
                    to_localise.append(item.latest)

        actions = []
        if to_localise:
            actions.append(menu.addAction(
                qta.icon('fa.cloud-download'),
                'Localise',
                partial(self.localise, to_localise)
            ))

        return actions


    def _add_multiple_packages_menu(self, menu, indexes):
        local_repo_table_index = get_local_repo_index() + 1
        model = self.model()

        actions = [
            self._add_delete_packages_menu(
                indexes, model, local_repo_table_index, menu
            )
        ]
        actions.extend(
            self._add_localise_package_menu(
                indexes, model, local_repo_table_index, menu
            )
        )

        if actions:
            menu.addSeparator()

    def on_delete_local(self, packages, all_version):
        delete_local(packages, all_version)
        self.packageDeleted.emit()

    def delete_empty_folder(self, folders):
        for folder in folders:
            shutil.rmtree(folder)
        self.packageDeleted.emit()

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

    def localise(self, packages):
        local_repo = config.get('local_packages_path')
        for package in packages:
            copy_package(package, local_repo, keep_timestamp=True)
        self.packageLocalised.emit()


class RezPackagesModel(QtGui.QStandardItemModel):

    def __init__(self, parent=None):
        self.repos = config.get('packages_path')
        super(RezPackagesModel, self).__init__(0, len(self.repos) + 1)
        self.setHorizontalHeaderLabels(['Package'] + self.repos)

    def reload(self):
        # TODO: #1 - keep scrolling position.

        package_repository_manager.clear_caches()
        self.setRowCount(0)

        for fam in packages.iter_package_families():
            row = [QtGui.QStandardItem(fam.name)]
            versions = [None]
            version_max = None

            # Fill the spreadsheet
            for repo in self.repos:
                latest = packages.get_latest_package(fam.name, paths=[repo])
                package_folder = os.path.join(repo, fam.name)

                item = QtGui.QStandardItem()
                item.latest = None
                item.empty_folder = None

                if not latest:
                    versions.append(None)
                    if os.path.isdir(os.path.join(repo, fam.name)):
                        item.empty_folder = package_folder
                else:
                    item.latest = latest

                    version_max = max(latest.version, version_max) \
                        if version_max else latest.version
                    versions.append(latest.version or None)

                item.setText(generate_item_text(item))
                item.setToolTip(generate_item_tooltip(item))
                row.append(item)


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
        view.setModel(model)
        return view
