# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p837_8.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import pandas as pd
from propakai import p837_8
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P837_8(unittest.TestCase):

    def test_rain_rate(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.837-7 Rp', header=None)
        lat_list = df.iloc[68:76, 2].to_list()
        lon_list = df.iloc[68:76, 3].to_list()
        r001_list = df.iloc[68:76, 5].to_list()
        for lat, lon, expected_r001 in zip(lat_list, lon_list, r001_list):
            r001 = p837_8.annual_rainfall_rate_001(lat, lon)
            self.assertTrue(isclose(r001, expected_r001))


if __name__ == '__main__':
    unittest.main()
