# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p2145_0.py.
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

from propakai import p2145_0


class Test_P2145_0(unittest.TestCase):

    def test_annual_stats(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.2145 CLIMATIC_MAPS_GAS_ATT', header=None)
        lat_list = df.iloc[22:101, 2].to_list()
        lon_list = df.iloc[22:101, 3].to_list()
        p_list = df.iloc[22:101, 5].to_list()
        mean_rho_list = df.iloc[22:101, 6].to_list()
        mean_P_list = df.iloc[22:101, 7].to_list()
        mean_T_list = df.iloc[22:101, 8].to_list()
        mean_V_list = df.iloc[22:101, 9].to_list()
        rho_list = df.iloc[22:101, 10].to_list()
        P_list = df.iloc[22:101, 11].to_list()
        T_list = df.iloc[22:101, 12].to_list()
        V_list = df.iloc[22:101, 13].to_list()

        for i in range(0, len(lat_list), 1):
            lat = lat_list[i]
            lon = lon_list[i]
            p = p_list[i]

            mean_rho = p2145_0.mean_surface_water_vapour_density(lat, lon)
            self.assertTrue(isclose(mean_rho, mean_rho_list[i]))

            mean_P = p2145_0.mean_surface_total_pressure(lat, lon)
            self.assertTrue(isclose(mean_P, mean_P_list[i]))

            mean_T = p2145_0.mean_surface_temperature(lat, lon)
            self.assertTrue(isclose(mean_T, mean_T_list[i]))

            mean_V = p2145_0.mean_integrated_water_vapour_content(lat, lon)
            self.assertTrue(isclose(mean_V, mean_V_list[i]))

            rho = p2145_0.surface_water_vapour_density(p, lat, lon)
            self.assertTrue(isclose(rho, rho_list[i]))

            P = p2145_0.surface_total_pressure(p, lat, lon)
            self.assertTrue(isclose(P, P_list[i]))

            T = p2145_0.surface_temperature(p, lat, lon)
            self.assertTrue(isclose(T, T_list[i]))

            V = p2145_0.integrated_water_vapour_content(p, lat, lon)
            self.assertTrue(isclose(V, V_list[i]))


    def test_weibull_params(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.2145 CLIMATIC_MAPS_GAS_ATT', header=None)
        lat_list = df.iloc[22:101, 15].to_list()
        lon_list = df.iloc[22:101, 16].to_list()
        k_VS_list = df.iloc[22:101, 18].to_list()
        lambda_VS_list = df.iloc[22:101, 19].to_list()
        for lat, lon, expected_k_VS, expected_lambda_VS in zip(lat_list, lon_list, k_VS_list,
                                                               lambda_VS_list):
            k_VS, lambda_VS = p2145_0.weibull_parameters(lat, lon)
            self.assertTrue(isclose(k_VS, expected_k_VS))
            self.assertTrue(isclose(lambda_VS, expected_lambda_VS))


    @unittest.skipUnless(environ.get('NO_SKIP'),
                         "Optional, requires several gigabytes of monthly stats")
    def test_monthly_stats(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.2145 CLIMATIC_MAPS_GAS_ATT', header=None)
        lat_list = df.iloc[109:188, 2].to_list()
        lon_list = df.iloc[109:188, 3].to_list()
        p_list = df.iloc[109:188, 5].to_list()
        months = [2,5,8,11]
        results = {'mean_rho':[], 'mean_P':[], 'mean_T':[], 'mean_V':[],
                   'rho':[], 'P':[], 'T':[], 'V':[]}
        for i in range(0, len(months)):
            results['mean_rho'].append(df.iloc[109:188, 7+i].to_list())
            results['mean_P'].append(df.iloc[109:188, 11+i].to_list())
            results['mean_T'].append(df.iloc[109:188, 15+i].to_list())
            results['mean_V'].append(df.iloc[109:188, 19+i].to_list())
            results['rho'].append(df.iloc[109:188, 23+i].to_list())
            results['P'].append(df.iloc[109:188, 27+i].to_list())
            results['T'].append(df.iloc[109:188, 31+i].to_list())
            results['V'].append(df.iloc[109:188, 35+i].to_list())

        for row_index, (lat, lon, p) in enumerate(zip(lat_list, lon_list, p_list)):
            for month_index, month in enumerate(months):

                mean_rho = p2145_0.mean_surface_water_vapour_density(lat, lon, month)
                self.assertTrue(isclose(mean_rho, results['mean_rho'][month_index][row_index]))

                mean_P = p2145_0.mean_surface_total_pressure(lat, lon, month)
                self.assertTrue(isclose(mean_P, results['mean_P'][month_index][row_index]))

                mean_T = p2145_0.mean_surface_temperature(lat, lon, month)
                self.assertTrue(isclose(mean_T, results['mean_T'][month_index][row_index]))

                mean_V = p2145_0.mean_integrated_water_vapour_content(lat, lon, month)
                self.assertTrue(isclose(mean_V, results['mean_V'][month_index][row_index]))

                rho = p2145_0.surface_water_vapour_density(p, lat, lon, month)
                self.assertTrue(isclose(rho, results['rho'][month_index][row_index]))

                P = p2145_0.surface_total_pressure(p, lat, lon, month)
                self.assertTrue(isclose(P, results['P'][month_index][row_index]))

                T = p2145_0.surface_temperature(p, lat, lon, month)
                self.assertTrue(isclose(T, results['T'][month_index][row_index]))

                V = p2145_0.integrated_water_vapour_content(p, lat, lon, month)
                self.assertTrue(isclose(V, results['V'][month_index][row_index]))


if __name__ == '__main__':
    unittest.main()
