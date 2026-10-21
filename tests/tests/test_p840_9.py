# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p840_9.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from os import environ
from math import isclose
import unittest
import pandas as pd

sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu

from propakai import p840_9


class Test_P839_4(unittest.TestCase):

    def test_slant_path_statistical_cloud_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.840-9 A_Clouds', header=None)
        lat_list = df.iloc[20:52, 2].to_list()
        lon_list = df.iloc[20:52, 3].to_list()
        p_list = df.iloc[20:52, 4].to_list()
        f_list = df.iloc[20:52, 5].to_list()
        theta_list = df.iloc[20:52, 6].to_list()
        Ac_list = df.iloc[20:52, 12].to_list()
        for lat, lon, p, f, theta, expected_Ac in zip(lat_list, lon_list, p_list, f_list,
                                                      theta_list, Ac_list):
            Ac = p840_9.slant_path_statistical_cloud_attenuation(f_ghz=f, theta_deg=theta,
                                                p_percent=p, lat=lat, lon=lon, month=None)
            self.assertTrue(isclose(Ac, expected_Ac))


    def test_log_normal_approx_to_stat_cloud_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.840-9 A_Clouds', header=None)
        lat_list = df.iloc[20:52, 14].to_list()
        lon_list = df.iloc[20:52, 15].to_list()
        p_list = df.iloc[20:52, 16].to_list()
        f_list = df.iloc[20:52, 17].to_list()
        theta_list = df.iloc[20:52, 18].to_list()
        Ac_list = df.iloc[20:52, 25].to_list()
        for lat, lon, p, f, theta, expected_Ac in zip(lat_list, lon_list, p_list, f_list,
                                                      theta_list, Ac_list):
            Ac = p840_9.log_normal_approx_to_stat_cloud_attenuation(f_ghz=f, theta_deg=theta,
                                                               p_percent=p, lat=lat, lon=lon)
            self.assertTrue(isclose(Ac, expected_Ac, rel_tol=1e-8))


    def test_integrated_cloud_liquid_water_content_annual(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P840_9_L', header=None)
        lat_list = df.iloc[23:59, 2].to_list()
        lon_list = df.iloc[23:59, 3].to_list()
        p_list = df.iloc[23:59, 4].to_list()
        L_list = df.iloc[23:59, 6].to_list()
        for lat, lon, p, expected_L in zip(lat_list, lon_list, p_list, L_list):
            L = p840_9.integrated_cloud_liquid_water_content(p_percent=p, lat=lat, lon=lon,
                                                             month=None)
            self.assertTrue(isclose(L, expected_L))


    @unittest.skipUnless(environ.get('NO_SKIP'),
                         "Optional, requires about 0.5 GB of monthly stats")
    def test_integrated_cloud_liquid_water_content_monthly(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P840_9_L', header=None)       
        lat_list = df.iloc[23:59, 11].to_list()
        lon_list = df.iloc[23:59, 12].to_list()
        p_list = df.iloc[23:59, 13].to_list()
        L_feb_list = df.iloc[23:59, 15].to_list()
        L_may_list = df.iloc[23:59, 16].to_list()
        L_aug_list = df.iloc[23:59, 17].to_list()
        L_nov_list = df.iloc[23:59, 18].to_list()
        for lat, lon, p, expect_L_feb, expect_L_may, expect_L_aug, expect_L_nov, in zip(lat_list,
            lon_list, p_list, L_feb_list, L_may_list, L_aug_list, L_nov_list):
            L_feb = p840_9.integrated_cloud_liquid_water_content(p_percent=p, lat=lat, lon=lon,
                                                                 month=2)
            L_may = p840_9.integrated_cloud_liquid_water_content(p_percent=p, lat=lat, lon=lon,
                                                                 month=5)
            L_aug = p840_9.integrated_cloud_liquid_water_content(p_percent=p, lat=lat, lon=lon,
                                                                 month=8)
            L_nov = p840_9.integrated_cloud_liquid_water_content(p_percent=p, lat=lat, lon=lon,
                                                                 month=11)
            self.assertTrue(isclose(L_feb, expect_L_feb, rel_tol=1e-7))
            self.assertTrue(isclose(L_may, expect_L_may, rel_tol=1e-7))
            self.assertTrue(isclose(L_aug, expect_L_aug, rel_tol=1e-7))
            self.assertTrue(isclose(L_nov, expect_L_nov, rel_tol=1e-7))


if __name__ == '__main__':
    unittest.main()
