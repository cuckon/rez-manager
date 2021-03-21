import os
import shutil
import logging
from functools import partial

import qtawesome as qta
from Qt import QtWidgets, QtCore
from rez.config import config

from .utils import catch_exception


def get_local_repo_index():
    packages_path = config.get('packages_path', [])
    local_packages_path = config.get('local_packages_path')
    if local_packages_path in packages_path:
        return packages_path.index(local_packages_path)
    return -1


def format_list(list_of_str):
    return '\n'.join(' - ' + line for line in list_of_str)


def delete_local(packages, all_version: bool):
    folders_deleted = []
    for package in packages:
        package_dir = os.path.join(package.resource.location, package.name)

        if all_version:
            to_delete = package_dir
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
        folders_deleted.append(to_delete)
    return folders_deleted


class SpreadsheetView(QtWidgets.QTreeView):
    packageDeleted = QtCore.Signal()
    # packageLocalised = QtCore.Signal()

    def __init__(self, parent=None):
        super(SpreadsheetView, self).__init__(parent)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.ExtendedSelection)
        self.logger = logging.getLogger(__name__)

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
                partial(self.delete_empty_folder, empty_package_folders)
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
                partial(self.model().localise, to_localise)
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

    @catch_exception
    def on_delete_local(self, packages, all_version):
        self.logger.info('Deleting..')
        folders_deleted = delete_local(packages, all_version)
        self.packageDeleted.emit()
        self.logger.info('Folder(s) deleted:\n' + format_list(folders_deleted))

    @catch_exception
    def delete_empty_folder(self, folders):
        self.logger.info('Deleting..')
        for folder in folders:
            shutil.rmtree(folder)
        self.logger.info('Folder(s) deleted:\n' + format_list(folders))
        self.packageDeleted.emit()

    @catch_exception
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

    # @catch_exception
    # def localise(self, packages):
    #     local_repo = config.get('local_packages_path')
    #     self.logger.info('Localising..')
    #     for package in packages:
    #         copy_package(package, local_repo, keep_timestamp=True)
    #     self.logger.info(f'{len(packages)} packages localised.')
    #     self.packageLocalised.emit()
