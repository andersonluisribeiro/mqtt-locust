import unittest
from utils import Utils

class UtilsTest(unittest.TestCase):

    def test_time_delta(self):
        self.assertEqual(Utils.time_delta(10, 10), 10)