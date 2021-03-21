import shutil
import os

import pytest
import rez.config

from rez_manager import views, models


ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def rez_tmp_folder(tmp_path):
    tmp_folder = f'{tmp_path}/rez_manager'
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
    os.mkdir(tmp_folder)

    yield tmp_folder

    shutil.rmtree(tmp_folder)


@pytest.fixture
def packages(rez_tmp_folder):
    local_repo = f'{rez_tmp_folder}/rez_manager/local'
    remote_repo = f'{rez_tmp_folder}/rez_manager/remote'

    config_content = dict(
        packages_path=[local_repo, remote_repo],
        local_packages_path=local_repo,
    )
    config = rez.config._create_locked_config(config_content)
    rez.config.config._swap(config)

    src_folder = os.path.join(ROOT, 'tests/data')
    for repo_folder in os.listdir(src_folder):
        shutil.copytree(
            os.path.join(src_folder, repo_folder),
            os.path.join(rez_tmp_folder, repo_folder),
        )

    yield

    rez.config.config._swap(config)


def test_views_get_local_repo_index(packages):
    assert views.get_local_repo_index() == 0


def test_models_update(qtbot, packages):
    model = models.RezPackagesModel()
    assert model.columnCount() == 3
