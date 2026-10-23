# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p839_4.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import pandas as pd
from propakai import p839_4
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P839_4(unittest.TestCase):

    def test_h0_hr(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.839-4 Rain_Height', header=None)
        lat_list = df.iloc[21:29, 2].to_list()
        lon_list = df.iloc[21:29, 3].to_list()
        h0_list = df.iloc[21:29, 5].to_list()
        hr_list = df.iloc[21:29, 6].to_list()
        for lat, lon, expected_h0, expected_hr in zip(lat_list, lon_list, h0_list, hr_list):
            h0 = p839_4.mean_annual_0c_isotherm_height(lat, lon)
            hr = p839_4.mean_annual_rain_height(lat, lon)
            self.assertTrue(isclose(h0, expected_h0))
            self.assertTrue(isclose(hr, expected_hr))


if __name__ == '__main__':
    unittest.main()
