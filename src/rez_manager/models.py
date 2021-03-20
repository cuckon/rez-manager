import os
import logging

from Qt import QtGui, QtCore
from rez import packages
from rez.config import config
from rez.package_repository import package_repository_manager

from .utils import catch_exception


def generate_item_tooltip(item):
    """Generate a proper tooltip for item"""
    if item.empty_folder:
        return '[Empty folder]'

    latest = item.latest
    if not latest:
        return ''

    tooltip = []

    if latest.description:
        tooltip.append(latest.format('Description: {description}'))
    if latest.variants:
        variants_string = ['Variants: ']

        # `latest.variants` Example:
        # [
        #   [PackageRequest('python-2.7')],
        #   [PackageRequest('python-3.7')],
        # ]
        for variant in latest.variants:
            variant_str = ' * '
            variant_str += ' | '.join(p.safe_str() for p in variant)
            variants_string.append(variant_str)
        tooltip.append('\n'.join(variants_string))
    if latest.tools:
        tooltip.append('Tools: ' + ', '.join(latest.tools))

    return '\n'.join(tooltip)


def generate_item_text(item):
    if item.latest:
        return str(item.latest.version)

    if item.empty_folder:
        return '-'

    return ''


class RezPackagesModel(QtGui.QStandardItemModel):
    cookingStarted = QtCore.Signal()
    cookingEnded = QtCore.Signal()

    def __init__(self, parent=None):
        self.repos = config.get('packages_path')
        super(RezPackagesModel, self).__init__(0, len(self.repos) + 1)
        self.setHorizontalHeaderLabels(['Package'] + self.repos)

        self.logger = logging.getLogger(__name__)

    @catch_exception
    def _make_row(self, row, family):
        self.setItem(row, 0, QtGui.QStandardItem(family.name))
        versions = [None]
        version_max = None

        # Fill the spreadsheet
        for irepo, repo in enumerate(self.repos):
            latest = packages.get_latest_package(family.name, paths=[repo])
            package_folder = os.path.join(repo, family.name)

            item = QtGui.QStandardItem()
            item.latest = None
            item.empty_folder = None

            if not latest:
                versions.append(None)
                if os.path.isdir(os.path.join(repo, family.name)):
                    item.empty_folder = package_folder
            else:
                item.latest = latest

                version_max = max(latest.version, version_max) \
                    if version_max else latest.version
                versions.append(latest.version or None)

            item.setText(generate_item_text(item))

            item.setToolTip(generate_item_tooltip(item))
            self.setItem(row, irepo + 1, item)

        # Find the winner
        winner_found = False
        for i in range(len(self.repos)):
            if (
                not winner_found and versions[i + 1] and
                versions[i + 1] == version_max
            ):
                winner_found = True
            else:
                self.item(row, i + 1).setForeground(QtGui.QColor('gray'))

    @catch_exception
    def reload(self):
        self.logger.info('Reloading..')
        package_repository_manager.clear_caches()
        families = list(packages.iter_package_families())
        self.setRowCount(len(families))

        for row, family in enumerate(families):
            self._make_row(row, family)

        self.logger.info(f'{len(families)} packages collected.')
