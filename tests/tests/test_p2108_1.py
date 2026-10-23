# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p2108_1.py.
Uses ITU validation examples file 'Clutter and BEL workbook_V2.xlsx' from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Software Products tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
from typing import cast
import pandas as pd
from propakai import p2108_1
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_2108_1(unittest.TestCase):

    def test_height_gain_terminal_correction(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CLUTTER_AND_BEL_WORKBOOK_V2)
        df = pd.read_excel(xlsx_file, sheet_name='Clutter Sect 3-1', header=None)

        f_ghz = cast(float, df.iloc[1, 3])
        h_m = cast(float, df.iloc[2, 3])
        ws_m = cast(float, df.iloc[3, 3])
        clut = p2108_1.ClutterType(cast(int, df.iloc[4, 3]))
        expected_Ah_db = cast(float, df.iloc[17, 3])
        Ah_db = p2108_1.height_gain_terminal_correction(f_ghz, h_m, clut, ws_m=ws_m)
        self.assertTrue(isclose(Ah_db, expected_Ah_db))

        f_ghz = cast(float, df.iloc[1, 4])
        h_m = cast(float, df.iloc[2, 4])
        ws_m = cast(float, df.iloc[3, 4])
        clut = p2108_1.ClutterType(cast(int, df.iloc[4, 4]))
        r_m = cast(float, df.iloc[5, 4])
        expected_Ah_db = cast(float, df.iloc[17, 4])
        Ah_db = p2108_1.height_gain_terminal_correction(f_ghz, h_m, clut, r_m=r_m, ws_m=ws_m)
        self.assertTrue(isclose(Ah_db, expected_Ah_db))


    def test_terrestrial_path_clutter_loss(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CLUTTER_AND_BEL_WORKBOOK_V2)
        df = pd.read_excel(xlsx_file, sheet_name='Clutter Sect 3-2', header=None)

        d_km = cast(float, df.iloc[4, 6])
        f_ghz_list = df.iloc[7:73, 5].to_list()
        p_percent_list = df.iloc[5, 11:15].to_list()

        for f_index, f_ghz in enumerate(f_ghz_list):
            for p_index, p_percent in enumerate(p_percent_list):
                expected_Lctt = cast(float, df.iloc[7+f_index, 11+p_index])
                Lctt = p2108_1.terrestrial_path_clutter_loss(f_ghz, d_km, p_percent)
                self.assertTrue(isclose(Lctt, expected_Lctt))


    def test_earth_space_clutter_loss(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CLUTTER_AND_BEL_WORKBOOK_V2)
        df = pd.read_excel(xlsx_file, sheet_name='Clutter Sect 3-3', header=None)

        f_ghz = cast(float, df.iloc[1, 3])
        p_percent_list = df.iloc[4:105, 5].to_list()
        theta_deg_list = df.iloc[3, 6:19].to_list()

        for p_index, p_percent in enumerate(p_percent_list):
            for theta_index, theta_deg in enumerate(theta_deg_list):
                expected_Lces = cast(float, df.iloc[4+p_index, 6+theta_index])
                Lces = p2108_1.earth_space_clutter_loss(f_ghz, theta_deg, p_percent)
                self.assertTrue(isclose(Lces, expected_Lces, rel_tol=1e-6))


if __name__ == '__main__':
    unittest.main()
