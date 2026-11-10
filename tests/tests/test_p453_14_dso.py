# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p453_14_dso.py.
NOTE: There is no Python wrapper yet for the C++ class for P.453-14, but this test class will allow
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
from propakai import p453_14
from propakai import _bin_utils as _bu
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P453_14(unittest.TestCase):

    def test_median_annual_nwet(self):
        p453_14._download_rec_data() # make sure rec data is present before running tests
        lib = _bu.get_dynamic_library('propakai_cpp')
        lib.P453_14_MedianAnnualNWet.argtypes = [ct.c_double, ct.c_double]
        lib.P453_14_MedianAnnualNWet.restype = ct.c_double

        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.453-14 Nwet', header=None)
        lat_list = df.iloc[20:28, 2].to_list()
        lon_list = df.iloc[20:28, 3].to_list()
        nwet_list = df.iloc[20:28, 5].to_list()
        for lat, lon, expected_nwet in zip(lat_list, lon_list, nwet_list):
            calculated_nwet = lib.P453_14_MedianAnnualNWet(lat, lon)
            self.assertTrue(isclose(calculated_nwet, expected_nwet))


if __name__ == '__main__':
    unittest.main()
