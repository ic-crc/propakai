# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p676_13.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from os import environ
from math import isclose, isnan
import unittest
import pandas as pd
from propakai import p676_13
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P676_13(unittest.TestCase):

    def test_gaseous_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 SpAtt', header=None)
        f_ghz_list = df.iloc[33:383, 2].to_list()
        gamma_o_list = df.iloc[33:383, 3].to_list()
        gamma_w_list = df.iloc[33:383, 4].to_list()
        gamma_list = df.iloc[33:383, 5].to_list()

        for i in range(0, len(f_ghz_list), 1):
            f_ghz = f_ghz_list[i]

            att = p676_13.gaseous_attenuation(f_ghz=f_ghz, p_hpa=1013.25, t_k=288.15, rho_gm3=7.5)
            self.assertTrue(isclose(att, gamma_list[i]))

            att = p676_13.dry_air_gaseous_attenuation(f_ghz=f_ghz, p_hpa=1013.25, t_k=288.15,
                                                      rho_gm3=7.5)
            self.assertTrue(isclose(att, gamma_o_list[i]))

            att = p676_13.water_vapour_gaseous_attenuation(f_ghz=f_ghz, p_hpa=1013.25, t_k=288.15,
                                                           rho_gm3=7.5)
            self.assertTrue(isclose(att, gamma_w_list[i]))


    def test_slant_path_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)

        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 A_Gas_A1_2.2.1a', header=None)
        expected_bend_rad = df.iloc[22:23, 26].to_list()[0]
        expected_att_db = df.iloc[22:23, 27].to_list()[0]
        att_db, bend_rad, _ = p676_13.slant_path_gaseous_attenuation(f_ghz=28, h1_km=0,
                                                                     h2_km=100.01, phi1_deg=30)
        self.assertTrue(isclose(bend_rad, expected_bend_rad))
        self.assertTrue(isclose(att_db, expected_att_db))

        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 A_Gas_A1_2.2.1b', header=None)
        expected_bend_rad = df.iloc[23:24, 30].to_list()[0]
        expected_att_db = df.iloc[23:24, 31].to_list()[0]
        att_db, bend_rad, _ = p676_13.slant_path_gaseous_attenuation(f_ghz=28, h1_km=1.3,
                                                                     h2_km=8, phi1_deg=30)
        self.assertTrue(isclose(bend_rad, expected_bend_rad))
        self.assertTrue(isclose(att_db, expected_att_db))

        expected_bend_rad = df.iloc[23:24, 62].to_list()[0]
        expected_att_db = df.iloc[23:24, 63].to_list()[0]
        att_db, bend_rad, _ = p676_13.slant_path_gaseous_attenuation(f_ghz=28, h1_km=1.3,
                                                                     h2_km=100, phi1_deg=30)
        self.assertTrue(isclose(bend_rad, expected_bend_rad))
        self.assertTrue(isclose(att_db, expected_att_db))


    def test_annex2_instantaneous_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 A_Gas_A2_INST', header=None)
        P_list = df.iloc[23:33, 2].to_list()
        T_list = df.iloc[23:33, 4].to_list()
        f_list = df.iloc[23:33, 5].to_list()
        rho_list = df.iloc[23:33, 8].to_list()
        theta_list = df.iloc[23:33, 9].to_list()
        Ao_zenith_list = df.iloc[23:33, 16].to_list()
        Ao_list = df.iloc[23:33, 17].to_list()
        Aw_zenith_list = df.iloc[23:33, 29].to_list()
        Aw_list = df.iloc[23:33, 30].to_list()

        for i in range(0, len(f_list), 1):
            Ao_zenith = p676_13.slant_path_instant_oxygen_gaseous_att(f_ghz=f_list[i], theta_deg=90,
                            ps_hpa=P_list[i], ts_k=T_list[i], rhows_gm3=rho_list[i])
            self.assertTrue(isclose(Ao_zenith, Ao_zenith_list[i]))

            Ao = p676_13.slant_path_instant_oxygen_gaseous_att(f_ghz=f_list[i],
                   theta_deg=theta_list[i], ps_hpa=P_list[i], ts_k=T_list[i], rhows_gm3=rho_list[i])
            self.assertTrue(isclose(Ao, Ao_list[i]))

            Aw_zenith = p676_13.slant_path_instant_water_vapour_gaseous_att_1(f_ghz=f_list[i],
                            theta_deg=90, ps_hpa=P_list[i], ts_k=T_list[i], rhows_gm3=rho_list[i])
            self.assertTrue(isclose(Aw_zenith, Aw_zenith_list[i]))

            Aw = p676_13.slant_path_instant_water_vapour_gaseous_att_1(f_ghz=f_list[i],
                   theta_deg=theta_list[i], ps_hpa=P_list[i], ts_k=T_list[i], rhows_gm3=rho_list[i])
            self.assertTrue(isclose(Aw, Aw_list[i]))


    def test_annex2_weibull_approx(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 A_Gas_A2_Weib', header=None)
        f_list = df.iloc[20:35, 7].to_list()
        lat_list = df.iloc[20:35, 2].to_list()
        lon_list = df.iloc[20:35, 3].to_list()
        p_list = df.iloc[20:35, 5].to_list()
        theta_list = df.iloc[20:35, 6].to_list()
        theta_list = pd.to_numeric(theta_list, errors='coerce')
        aw_zenith_list = df.iloc[20:35, 18].to_list()
        aw_list = df.iloc[20:35, 19].to_list()
        aw_list = pd.to_numeric(aw_list, errors='coerce')

        for i in range(0, len(f_list), 1):
            aw_zenith = p676_13.weibull_approximation(f_ghz=f_list[i], theta_deg=90,
                            p_percent=p_list[i], lat=lat_list[i], lon=lon_list[i], h_mamsl=None)
            self.assertTrue(isclose(aw_zenith, aw_zenith_list[i]))

            if isnan(theta_list[i]) is False:
                aw = p676_13.weibull_approximation(f_ghz=f_list[i], theta_deg=theta_list[i],
                         p_percent=p_list[i], lat=lat_list[i], lon=lon_list[i], h_mamsl=None)
                self.assertTrue(isclose(aw, aw_list[i]))


    def test_annex2_annual_statistical_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 A_Gas_A2_STAT', header=None)
        lat_list = df.iloc[23:100, 2].to_list()
        lon_list = df.iloc[23:100, 3].to_list()
        f_list = df.iloc[23:100, 6].to_list()
        theta_list = df.iloc[23:100, 8].to_list()
        percent_list = df.iloc[23:100, 13].to_list()
        Ao_zenith_list = df.iloc[23:100, 23].to_list()
        Ao_list = df.iloc[23:100, 24].to_list()
        Aw_zenith_list = df.iloc[23:100, 38].to_list()
        Aw_list = df.iloc[23:100, 39].to_list()
        Agas_list = df.iloc[23:100, 41].to_list()

        for i in range(0, len(f_list), 1):
            Ao_zenith = p676_13.slant_path_statistical_oxygen_gaseous_att(f_ghz=f_list[i],
                            theta_deg=90, p_percent=percent_list[i], lat=lat_list[i],
                            lon=lon_list[i], month=None, h_mamsl=None)
            self.assertTrue(isclose(Ao_zenith, Ao_zenith_list[i]))

            Ao = p676_13.slant_path_statistical_oxygen_gaseous_att(f_ghz=f_list[i],
                     theta_deg=theta_list[i], p_percent=percent_list[i], lat=lat_list[i],
                     lon=lon_list[i], month=None, h_mamsl=None)
            self.assertTrue(isclose(Ao, Ao_list[i]))

            Aw_zenith = p676_13.slant_path_statistical_water_vapour_gaseous_att(f_ghz=f_list[i],
                            theta_deg=90, p_percent=percent_list[i], lat=lat_list[i],
                            lon=lon_list[i], month=None, h_mamsl=None)
            self.assertTrue(isclose(Aw_zenith, Aw_zenith_list[i]))

            Aw = p676_13.slant_path_statistical_water_vapour_gaseous_att(f_ghz=f_list[i],
                     theta_deg=theta_list[i], p_percent=percent_list[i], lat=lat_list[i],
                     lon=lon_list[i], month=None, h_mamsl=None)
            self.assertTrue(isclose(Aw, Aw_list[i]))

            Agas = p676_13.slant_path_statistical_gaseous_attenuation(f_ghz=f_list[i],
                       theta_deg=theta_list[i], p_percent=percent_list[i], lat=lat_list[i],
                       lon=lon_list[i], month=None, h_mamsl=None)
            self.assertTrue(isclose(Agas, Agas_list[i]))


    @unittest.skipUnless(environ.get('NO_SKIP'),
                         "Optional, requires several gigabytes of monthly stats")
    def test_annex2_monthly_statistical_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.676-13 A_Gas_A2_STAT', header=None)
        lat_list = df.iloc[110:187, 2].to_list()
        lon_list = df.iloc[110:187, 3].to_list()
        f_list = df.iloc[110:187, 6].to_list()
        month_list = df.iloc[110:187, 7].to_list()
        theta_list = df.iloc[110:187, 9].to_list()
        percent_list = df.iloc[110:187, 14].to_list()
        Ao_zenith_list = df.iloc[110:187, 24].to_list()
        Ao_list = df.iloc[110:187, 25].to_list()
        Aw_zenith_list = df.iloc[110:187, 39].to_list()
        Aw_list = df.iloc[110:187, 40].to_list()
        Agas_list = df.iloc[110:187, 42].to_list()

        for i in range(0, len(f_list), 1):
            Ao_zenith = p676_13.slant_path_statistical_oxygen_gaseous_att(f_ghz=f_list[i],
                            theta_deg=90, p_percent=percent_list[i], lat=lat_list[i],
                            lon=lon_list[i], month=month_list[i], h_mamsl=None)
            self.assertTrue(isclose(Ao_zenith, Ao_zenith_list[i]))

            Ao = p676_13.slant_path_statistical_oxygen_gaseous_att(f_ghz=f_list[i],
                     theta_deg=theta_list[i], p_percent=percent_list[i], lat=lat_list[i],
                     lon=lon_list[i], month=month_list[i], h_mamsl=None)
            self.assertTrue(isclose(Ao, Ao_list[i]))

            Aw_zenith = p676_13.slant_path_statistical_water_vapour_gaseous_att(f_ghz=f_list[i],
                            theta_deg=90, p_percent=percent_list[i], lat=lat_list[i],
                            lon=lon_list[i], month=month_list[i], h_mamsl=None)
            self.assertTrue(isclose(Aw_zenith, Aw_zenith_list[i]))

            Aw = p676_13.slant_path_statistical_water_vapour_gaseous_att(f_ghz=f_list[i],
                     theta_deg=theta_list[i], p_percent=percent_list[i], lat=lat_list[i],
                     lon=lon_list[i], month=month_list[i], h_mamsl=None)
            self.assertTrue(isclose(Aw, Aw_list[i]))

            Agas = p676_13.slant_path_statistical_gaseous_attenuation(f_ghz=f_list[i],
                       theta_deg=theta_list[i], p_percent=percent_list[i], lat=lat_list[i],
                       lon=lon_list[i], month=month_list[i], h_mamsl=None)
            self.assertTrue(isclose(Agas, Agas_list[i]))


if __name__ == '__main__':
    unittest.main()
