# -*- coding: utf-8 -*-

name = 'manager'

authors = ['John Su']

version = '0.0.1'

requires = [
    'rez',
    'qt_py',
    'PyQt5',
]

tools = [
    'manager',
]


def commands():
    env.PYTHONPATH.append('{root}/pythonpath')
    env.PATH.append('{root}/path')
    env.MANAGER_RESOURCES_FOLDER = '{root}/resources'

    alias('manager', 'python -m rez_manager')
