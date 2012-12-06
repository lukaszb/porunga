import datetime
from porunga.utils.backports import get_total_seconds
from porunga.utils.compat import unittest


class TestGetTotalSeconds(unittest.TestCase):

    def assertTotalSecondsEqual(self, timedelta, expected_seconds):
        result = get_total_seconds(timedelta)
        self.assertEqual(result, expected_seconds,
            "We computed %s seconds for %s but expected %s"
            % (result, timedelta, expected_seconds))

    def test_get_total_seconds_returns_proper_value(self):
        self.assertTotalSecondsEqual(datetime.timedelta(seconds=1001), 1001)

    def test_get_total_seconds_returns_proper_value_for_partial_seconds(self):
        self.assertTotalSecondsEqual(datetime.timedelta(seconds=50.65), 50.65)


