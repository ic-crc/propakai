# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p2148_0.py.
Compares with results from ITU Geodata Catalog:
https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.2148-0-202208
"""
from math import isclose
import unittest

from propakai import p2148_0
from propakai.geo_catalog import gc_p2148_0


class Test_P2148_0(unittest.TestCase):

    def test_wind_speed(self):
        locations = [(0,0), (45,-75), (-45,-75), (45,75), (-45,75)]
        p_percents = [0.01, 0.1, 1, 10, 99]
        for location in locations:
            for p in p_percents:
                lat = location[0]
                lon = location[1]
                w = p2148_0.wind_speed(p, lat, lon)
                expected_w =  gc_p2148_0.average_annual_wind_speed(lat, lon, p)
                self.assertTrue(isclose(w, expected_w))


if __name__ == '__main__':
    unittest.main()
