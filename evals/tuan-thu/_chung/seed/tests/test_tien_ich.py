import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import tien_ich


class TienIchTest(unittest.TestCase):
    def test_gop_ten(self):
        self.assertEqual(tien_ich.gop_ten("Nguyễn", "An"), "Nguyễn An")

    def test_dem_tu(self):
        self.assertEqual(tien_ich.dem_tu("một hai ba"), 3)


if __name__ == "__main__":
    unittest.main()
