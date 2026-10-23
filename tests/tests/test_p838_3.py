# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p838_3.py.
Uses ITU validation examples file CG-3M3J-13-ValEx-Rev8.3.0.xlsx from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import pandas as pd
from propakai import p838_3
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_P838_3(unittest.TestCase):

    def test_coeffs_and_rain_attenuation(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CG_3M3J_13_VALEX_REV830)
        df = pd.read_excel(xlsx_file, sheet_name='P.838-3 Sp.Att', header=None)
        theta_list = df.iloc[19:83, 5].to_list()
        f_list = df.iloc[19:83, 6].to_list()
        r_list = df.iloc[19:83, 7].to_list()
        tau_list = df.iloc[19:83, 8].to_list()
        k_list = df.iloc[19:83, 13].to_list()
        a_list = df.iloc[19:83, 14].to_list()
        gamma_r_list = df.iloc[19:83, 15].to_list()
        for theta, f, r, tau, k, a, gamma_r in zip(theta_list, f_list, r_list, tau_list,
                                                   k_list, a_list, gamma_r_list):
            calculated_k, calculated_a = p838_3.coefficients(f_ghz=f, theta_deg=theta, tau_deg=tau)
            calculated_gamma_r = p838_3.rain_attenuation(f_ghz=f, r_mmhr=r, theta_deg=theta,
                                                         tau_deg=tau)
            self.assertTrue(isclose(calculated_k, k))
            self.assertTrue(isclose(calculated_a, a))
            self.assertTrue(isclose(calculated_gamma_r, gamma_r))


if __name__ == '__main__':
    unittest.main()
