# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for "p1511_3_dso.py".
NOTE: There is no Python wrapper yet for the C++ class for P.1511-3, but this test class will allow
us to easily test the C++ implementation.

Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import ctypes as ct
import pandas as pd
from propakai import _bin_utils as _bu
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P1511_3(unittest.TestCase):

    def test_topo_height(self):
        lib = _bu.get_dynamic_library('propakai_cpp')
        lib.P1511_3_TopographicHeight.argtypes = [ct.c_double, ct.c_double]
        lib.P1511_3_TopographicHeight.restype = ct.c_double

        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.1511 TOPO', header=None)
        lat_list = df.iloc[22:37, 2].to_list()
        lon_list = df.iloc[22:37, 3].to_list()
        hs_list = df.iloc[22:37, 4].to_list()
        for lat, lon, expected_hs in zip(lat_list, lon_list, hs_list):
            hs = lib.P1511_3_TopographicHeight(lat, lon)
            self.assertTrue(isclose(hs, expected_hs))


    def test_geoid_undulation(self):
        lib = _bu.get_dynamic_library('propakai_cpp')
        lib.P1511_3_GeoidUndulation.argtypes = [ct.c_double, ct.c_double]
        lib.P1511_3_GeoidUndulation.restype = ct.c_double

        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.1511 TOPO', header=None)
        lat_list = df.iloc[22:37, 6].to_list()
        lon_list = df.iloc[22:37, 7].to_list()
        h_egm2008_list = df.iloc[22:37, 8].to_list()
        print('')
        for lat, lon, expected_h_egm2008 in zip(lat_list, lon_list, h_egm2008_list):
            h_egm2008 = lib.P1511_3_GeoidUndulation(lat, lon)
            self.assertTrue(isclose(h_egm2008, expected_h_egm2008))


if __name__ == '__main__':
    unittest.main()
