# -*- coding: utf-8 -*-

name = 'rez_manager'

authors = ['John Su']

version = '1.0.1'

uuid = 'johnsu.rez-manager'

requires = [
    'rez',
    'PyQt5',
    'python-3',
    'QtAwesome-0.7.3',
]

tools = [
    'manager',
]

tests = {
    'test': {
        'command': 'pytest',
        'requires': ['python-3', 'pytest', 'pytest_qt'],
    },
}


def commands():

    env.PYTHONPATH.append('{root}/src')
    env.PYTHONPATH.append('{root}/vendors')
    env.PATH.append('{root}/path')
    env.MANAGER_RESOURCES_FOLDER = '{root}/resources'

    alias('manager', 'python -m rez_manager')
