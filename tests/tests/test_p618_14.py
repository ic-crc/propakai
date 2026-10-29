# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p618_14.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
from typing import cast
import pandas as pd
from propakai import p618_14
from propakai import p837_8
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P618_14(unittest.TestCase):

    def test_rain_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.618-14 A_Rain', header=None)
        lat_list = df.iloc[22:86, 2].to_list()
        lon_list = df.iloc[22:86, 3].to_list()
        hs_list = df.iloc[22:86, 5].to_list()
        f_list = df.iloc[22:86, 6].to_list()
        theta_list = df.iloc[22:86, 7].to_list()
        tau_list = df.iloc[22:86, 8].to_list()
        p_list = df.iloc[22:86, 9].to_list()
        r001_list = df.iloc[22:86, 11].to_list()
        Ap_list = df.iloc[22:86, 20].to_list()
        for lat, lon, hs, f, theta, tau, p, r001, expected_Ap in zip(lat_list, lon_list, hs_list,
                                        f_list, theta_list, tau_list, p_list, r001_list, Ap_list):

            # NOTE 1: The rainfall rate (R001) in the ITU Excel document is calculated using the
            # method of Annex 1 from ITU-R P.837 (requires monthly data).
            # p837_8.annual_rainfall_rate() uses this aforementioned method while
            # p837_8.annual_rainfall_rate_001() uses a bi-linear interpolation of pre-computed
            # values in the R001.txt digital map.
            digital_map_r001 = p837_8.annual_rainfall_rate_001(lat, lon)
            self.assertTrue(isclose(digital_map_r001, r001, rel_tol=1e-3))
            computed_r001, _p0_annual = p837_8.annual_rainfall_rate(0.01, lat, lon)
            self.assertTrue(isclose(computed_r001, r001, rel_tol=1e-5))

            Ap = p618_14.rain_attenuation(f, theta, p, lat, lon, tau, None, r001)
            self.assertTrue(isclose(Ap, expected_Ap))
            Ap = p618_14.rain_attenuation(f, theta, p, lat, lon, tau, hs, r001)
            self.assertTrue(isclose(Ap, expected_Ap))


    def test_scintillation_fading(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.618-14 A_Scint', header=None)
        lat_list = df.iloc[20:68, 2].to_list()
        lon_list = df.iloc[20:68, 3].to_list()
        f_list = df.iloc[20:68, 6].to_list()
        theta_list = df.iloc[20:68, 7].to_list()
        d_list = df.iloc[20:68, 8].to_list()
        eta_list = df.iloc[20:68, 9].to_list()
        p_list = df.iloc[20:68, 10].to_list()
        As_list = df.iloc[20:68, 17].to_list()

        for lat, lon, theta, d, f, eta, p, expected_As in zip(lat_list, lon_list, theta_list,
                                                  d_list, f_list, eta_list, p_list, As_list):
            As = p618_14.scintillation_fading(f, theta, p, lat, lon, d, eta)
            self.assertTrue(isclose(As, expected_As))


    def test_total_atmospheric_attenuation_1(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.618-14 Att_Tot', header=None)
        lat_list = df.iloc[25:73, 2].to_list()
        lon_list = df.iloc[25:73, 3].to_list()
        hs_list = df.iloc[25:73, 4].to_list()
        f_list = df.iloc[25:73, 6].to_list()
        theta_list = df.iloc[25:73, 7].to_list()
        d_list = df.iloc[25:73, 8].to_list()
        eta_list = df.iloc[25:73, 9].to_list()
        tau_list = df.iloc[25:73, 10].to_list()
        p_list = df.iloc[25:73, 11].to_list()
        AG_list = df.iloc[25:73, 14].to_list()
        AC_list = df.iloc[25:73, 15].to_list()
        AR_list = df.iloc[25:73, 16].to_list()
        AS_list = df.iloc[25:73, 17].to_list()
        AT_list = df.iloc[25:73, 18].to_list()
        for lat, lon, hs, f, theta, d, eta, tau, p, expect_AG, expect_AC, expect_AR, expect_AS, \
            expect_AT in zip(lat_list, lon_list, hs_list, f_list, theta_list, d_list, eta_list,
                             tau_list, p_list, AG_list, AC_list, AR_list, AS_list, AT_list):

            computed_r001, _p0_annual = p837_8.annual_rainfall_rate(0.01, lat, lon) # see NOTE 1
            AR1 = p618_14.rain_attenuation(f, theta, p, lat, lon, tau, None, computed_r001)
            AR2 = p618_14.rain_attenuation(f, theta, p, lat, lon, tau, hs, computed_r001)
            self.assertTrue(isclose(AR1, expect_AR, rel_tol=1e-5))
            self.assertTrue(isclose(AR2, expect_AR, rel_tol=1e-5))

            AC = p618_14.cloud_attenuation(f, theta, max(p,5),  lat, lon)
            self.assertTrue(isclose(AC, expect_AC, rel_tol=1e-7))

            AG1 = p618_14.gaseous_attenuation(f, theta, max(p,5), lat, lon, None)
            AG2 = p618_14.gaseous_attenuation(f, theta, max(p,5), lat, lon, hs)
            self.assertTrue(isclose(AG1, expect_AG))
            self.assertTrue(isclose(AG2, expect_AG))

            AS = p618_14.scintillation_fading(f, theta, p, lat, lon, d, eta)
            self.assertTrue(isclose(AS, expect_AS))

            AT, AR, AC, AG, AS = p618_14.total_atmospheric_attenuation(f, theta, p, lat, lon, tau,
                                                                d, eta, hs, False, computed_r001)
            self.assertTrue(isclose(AT, expect_AT, rel_tol=1e-5))
            self.assertTrue(isclose(AR, expect_AR, rel_tol=1e-5))
            self.assertTrue(isclose(AC, expect_AC, rel_tol=1e-7))
            self.assertTrue(isclose(AG, expect_AG))
            self.assertTrue(isclose(AS, expect_AS))


    def test_total_atmospheric_attenuation_2(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.618-14 Att_Tot', header=None)
        lat = cast(float, df.iloc[80, 2])
        lon = cast(float, df.iloc[80, 3])
        hs = cast(float, df.iloc[80, 4])
        f = cast(float, df.iloc[80, 6])
        theta = cast(float, df.iloc[80, 7])
        d = cast(float, df.iloc[80, 8])
        eta = cast(float, df.iloc[80, 9])
        tau = cast(float, df.iloc[80, 10])
        p_list = df.iloc[87:107, 2].to_list()
        AS_list = df.iloc[87:107, 5].to_list()
        AR_list = df.iloc[87:107, 6].to_list()
        AC_list = df.iloc[87:107, 7].to_list()
        AG_list = df.iloc[87:107, 8].to_list()
        AT_list = df.iloc[87:107, 10].to_list()
        for p, expect_AG, expect_AC, expect_AR, expect_AS, expect_AT in zip(p_list, AG_list,
                                                        AC_list, AR_list, AS_list, AT_list):

            # not specifying r001, will use digital map
            AT, AR, AC, AG, AS = p618_14.total_atmospheric_attenuation(f, theta, p, lat, lon, tau,
                                                                       d, eta, hs)
            self.assertTrue(isclose(AT, expect_AT, rel_tol=1e-3)) # increased error from digital map usage
            self.assertTrue(isclose(AR, expect_AR, rel_tol=1e-3)) # increased error from digital map usage
            self.assertTrue(isclose(AC, expect_AC, rel_tol=1e-7))
            self.assertTrue(isclose(AG, expect_AG))
            self.assertTrue(isclose(AS, expect_AS))


    def test_hydrometeor_cross_pol_discrimination(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.618-14 XPD', header=None)
        p_list = df.iloc[20:84, 6].to_list()
        f_list = df.iloc[20:84, 7].to_list()
        theta_list = df.iloc[20:84, 8].to_list()
        tau_list = df.iloc[20:84, 9].to_list()
        ap_list = df.iloc[20:84, 10].to_list()
        xpd_list = df.iloc[20:84, 19].to_list()
        for p, f, theta, tau, ap, expected_xpd in zip(p_list, f_list, theta_list, tau_list,
                                                      ap_list, xpd_list):
            xpd = p618_14.hydrometeor_cross_pol_discrimination(f, theta, p, tau, ap)
            self.assertTrue(isclose(xpd, expected_xpd))


if __name__ == '__main__':
    unittest.main()
