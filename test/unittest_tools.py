import unittest

from src.tools import Tools


class Unittest(unittest.TestCase):
    def setUp(self):
        self.tools = Tools()

    def test_get_utc_epoch(self):
        date = '14.05.2018'
        result = self.tools.get_utc_epoch(date)
        self.assertEqual(1526256000000, result)