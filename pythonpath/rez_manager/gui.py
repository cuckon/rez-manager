import os
from functools import partial

from Qt import QtWidgets, QtGui, QtCore
from rez import packages
from rez.config import config


def generate_tooltip(package):
    """Generate a proper tooltip for item"""
    tooltip = [package.format(
        '<h1>{name}</h1>'
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


def delete_local(packages, all_version):
    print(packages, all_version)


def _add_delete_local_menu(menu, model, indexes):
    local_repo_table_index = get_local_repo_index() + 1
    to_delete = []
    for index in indexes:
        if index.column() == local_repo_table_index:
            item = model.itemFromIndex(index)
            version = item.text()
            if version:
                to_delete.append(item.latest)

    if to_delete:
        menu.addAction(
            'Delete Local Package',
            partial(delete_local, to_delete, False)
        )
        menu.addAction(
            'Delete Local Package(All Versions)',
            partial(delete_local, to_delete, True)
        )
        menu.addSeparator()


class SpreadsheetView(QtWidgets.QTreeView):
    def selectedItem(self):
        indexes = self.selectionModel().selectedIndexes()
        for i in indexes:
            print(i.row(), i.column())
        return indexes[0] if indexes else None

    def update(self):
        # TODO: implement this
        print('Update')

    def contextMenuEvent(self, event):
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            return

        menu = QtWidgets.QMenu(self)
        model = self.model()

        _add_delete_local_menu(menu, model, indexes)
        menu.addAction('Update', self.update)
        menu.exec(event.globalPos())


class ManagerWin(QtWidgets.QMainWindow):
    """Main window class."""
    def __init__(self):
        super(ManagerWin, self).__init__()
        self.repos = []

        self.setup_ui()

        self.spreadsheet = self.setup_spreadsheet()
        self.centralWidget().layout().addWidget(self.spreadsheet)

        self.update_spreadsheet()

    def setup_ui(self):
        """Do the general ui setup work."""
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QVBoxLayout())
        self.setCentralWidget(central_widget)

        self.setWindowTitle('Rez Packages Manager')
        icon_path = os.path.join(
            os.environ['MANAGER_RESOURCES_FOLDER'], 'icon.png'
        )
        self.setWindowIcon(QtGui.QIcon(icon_path))


    def setup_spreadsheet(self):
        view = SpreadsheetView()
        self.repos = config.get('packages_path')
        model = QtGui.QStandardItemModel(0, len(self.repos) + 1)
        model.setHorizontalHeaderLabels(['Package'] + self.repos)

        view.setModel(model)
        return view

    def update_spreadsheet(self):
        """Update the spreadsheet."""

        # TODO Extract this model into RezModel

        model = self.spreadsheet.model()
        model.setRowCount(0)

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

            model.appendRow(row)
