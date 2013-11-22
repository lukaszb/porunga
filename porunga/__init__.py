"""
porunga is a test framework for simple algorithms
"""
import os
import sys


VERSION = (0, 9, 3)

__version__ = '.'.join((str(each) for each in VERSION[:4]))

def get_version():
    """
    Returns shorter version (digit parts only) as string.
    """
    version = '.'.join((str(each) for each in VERSION[:3]))
    if len(VERSION) > 3:
        version += VERSION[3]
    return version

def update_sys_path():
    dirpath = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, dirpath)

def get_manager():
    update_sys_path()
    from monolith.cli import ExecutionManager
    from porunga.utils.imports import import_class

    class PorungaManager(ExecutionManager):

        def get_commands_to_register(self):
            registry = {
                'test': 'porunga.commands.test.PorungaTestCommand',
            }
            commands = dict((name, import_class(path)) for name, path in
                registry.items())
            return commands

    return PorungaManager(['porunga'])


def main():
    manager = get_manager()
    manager.execute()

