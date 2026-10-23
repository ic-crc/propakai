# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p1510_1.py.

Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)

Compares with results from ITU Geodata Catalog:
https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.1510-1-201706
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import pandas as pd
from propakai import p1510_1
from propakai.geo_catalog import gc_p1510_1
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P1510_1(unittest.TestCase):

    def test_temperature(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.1510 Surf_temp', header=None)
        lat_list = df.iloc[23:38, 2].to_list()
        lon_list = df.iloc[23:38, 3].to_list()
        t_lists = [[]]*13
        for month in range(0, 13):
            t_list = df.iloc[23:38, month+4].to_list()
            t_lists[month] = t_list
        for month, t_list in enumerate(t_lists):
            for lat, lon, expected_t in zip(lat_list, lon_list, t_list):
                if month == 0:
                    t = p1510_1.mean_surface_temperature(lat, lon)
                else:
                    t = p1510_1.mean_surface_temperature(lat, lon, month)
                self.assertTrue(isclose(t, expected_t))


    def test_temperature_against_geocatalog(self):
        locations = [(0,0), (45,-75), (-45,-75), (45,75), (-45,75)]
        months = [None, 1, 6, 12]
        for location in locations:
            for month in months:
                lat = location[0]
                lon = location[1]
                t = p1510_1.mean_surface_temperature(lat, lon, month)
                if month is None:
                    expected_t =  gc_p1510_1.annual_mean_surface_temperature(lat, lon)
                else:
                    expected_t =  gc_p1510_1.monthly_mean_surface_temperature(lat, lon, month)
                self.assertTrue(isclose(t, expected_t))


if __name__ == '__main__':
    unittest.main()
