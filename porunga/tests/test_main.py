import unittest
from porunga import get_manager
from porunga.commands.test import PorungaTestCommand


class TestManager(unittest.TestCase):

    def test_manager_has_proper_commands(self):
        manager = get_manager()
        commands = manager.get_commands()

        self.assertTrue('test' in commands)
        test_command = commands['test']
        self.assertTrue(isinstance(test_command, PorungaTestCommand))

