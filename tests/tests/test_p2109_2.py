# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p2109_2.py.
Uses ITU validation examples file 'Clutter and BEL workbook_V2.xlsx' from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Software Products tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import pandas as pd
from propakai import p2109_2
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_2109_2(unittest.TestCase):

    def test_building_entry_loss(self):
        xlsx_file = _tu.get_pathname(_tu.ValidationFile.CLUTTER_AND_BEL_WORKBOOK_V2)
        df = pd.read_excel(xlsx_file, sheet_name='BEL', header=None)
        f_ghz = df.iloc[10, 1]
        theta_deg = df.iloc[10, 2]
        assert isinstance(f_ghz, (int, float))
        assert isinstance(theta_deg, (int, float))
        p_percent_list = df.iloc[14:156, 1].to_list()
        bel_trad_list = df.iloc[14:156, 9].to_list()
        bel_eff_list = df.iloc[14:156, 16].to_list()
        TRAD = p2109_2.BuildingType.TRADITIONAL
        EFF = p2109_2.BuildingType.THERMALLY_EFFICIENT
        for p_percent, expected_bel_trad, expected_bell_eff in zip(p_percent_list, bel_trad_list,
                                                                   bel_eff_list):
            bel_trad = p2109_2.building_entry_loss(f_ghz, theta_deg, p_percent, TRAD)
            bel_eff = p2109_2.building_entry_loss(f_ghz, theta_deg, p_percent, EFF)
            self.assertTrue(isclose(bel_trad, expected_bel_trad, rel_tol=1e-4))
            self.assertTrue(isclose(bel_eff, expected_bell_eff, rel_tol=1e-7))


if __name__ == '__main__':
    unittest.main()
