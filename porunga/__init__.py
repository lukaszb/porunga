"""
porunga is a test framework for simple algorithms
"""
import os
import sys


VERSION = (0, 8, 1)

__version__ = '.'.join((str(each) for each in VERSION[:4]))

def get_version():
    """
    Returns shorter version (digit parts only) as string.
    """
    return '.'.join((str(each) for each in VERSION[:4]))

def update_sys_path():
    dirpath = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, dirpath)

def main():
    update_sys_path()
    from monolith.cli import ExecutionManager
    from porunga.utils.imports import import_class

    class ForfiterManager(ExecutionManager):

        def get_commands_to_register(self):
            registry = {
                'test': 'porunga.commands.test.TestCommand',
            }
            commands = dict((name, import_class(path)) for name, path in
                registry.items())
            return commands

    manager = ForfiterManager(['porunga'])
    manager.execute()

