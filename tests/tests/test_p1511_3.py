# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p1511_3.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import pandas as pd

sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu

from propakai import p1511_3


class Test_P1511_3(unittest.TestCase):

    def test_topo_height(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.1511 TOPO', header=None)
        lat_list = df.iloc[22:37, 2].to_list()
        lon_list = df.iloc[22:37, 3].to_list()
        hs_list = df.iloc[22:37, 4].to_list()
        for lat, lon, expected_hs in zip(lat_list, lon_list, hs_list):
            hs = p1511_3.topographic_height(lat, lon)
            self.assertTrue(isclose(hs, expected_hs))


    def test_geoid_undulation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.1511 TOPO', header=None)
        lat_list = df.iloc[22:37, 6].to_list()
        lon_list = df.iloc[22:37, 7].to_list()
        h_egm2008_list = df.iloc[22:37, 8].to_list()
        for lat, lon, expected_h_egm2008 in zip(lat_list, lon_list, h_egm2008_list):
            h_egm2008 = p1511_3.geoid_undulation(lat, lon)
            self.assertTrue(isclose(h_egm2008, expected_h_egm2008))


if __name__ == '__main__':
    unittest.main()
