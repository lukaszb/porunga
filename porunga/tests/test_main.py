import unittest
from porunga import get_manager
from porunga.commands.test import PorungaTestCommand


class TestManager(unittest.TestCase):

    def test_manager_has_proper_commands(self):
        manager = get_manager()
        commands = manager.get_commands()

        self.assertIn('test', commands)
        test_command = commands['test']
        self.assertIsInstance(test_command, PorungaTestCommand)

