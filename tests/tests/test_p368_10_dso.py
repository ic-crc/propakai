# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p368_10_dso.py.
Uses validation examples obtained from:
https://github.com/eeveetza/LFMFSmoothEarth
"""
from os.path import dirname, abspath, join
from math import isclose
import unittest
import csv
from propakai import p368_10_dso


class Test_368_10_dso(unittest.TestCase):

    def test_basic_transmission_loss(self):
        script_dir = dirname(abspath(__file__))
        pathname = join(script_dir, 'validation_data', 'p368_10',
                        'ValidationExampleLFMFSmoothEarth.csv')
        with open(pathname, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                a_db, e_dbuvm, p_dbm, method = p368_10_dso.basic_transmission_loss(
                    f_mhz = float(row['f__mhz']),
                    d_km = float(row['d__km']),
                    htx_m = float(row['h_tx__meter']),
                    hrx_m = float(row['h_rx__meter']),
                    ptx_w = float(row['P_tx__watt']),
                    pol = p368_10_dso.Polarization(int(row['pol'])),
                    ns = float(row['N_s']),
                    eps = float(row['epsilon']),
                    sigma_sm = float(row['sigma '])
                )

                expected_a_db = float(row['A_btl__db'])
                self.assertTrue(isclose(a_db, expected_a_db, rel_tol=1e-9, abs_tol=1e-6))

                expected_e_dbuvm = float(row['E_dBuVm'])
                self.assertTrue(isclose(e_dbuvm, expected_e_dbuvm, rel_tol=1e-9, abs_tol=1e-6))

                expected_p_dbm = float(row['P_rx__dbm'])
                self.assertTrue(isclose(p_dbm, expected_p_dbm, rel_tol=1e-9, abs_tol=1e-6))

                expected_method = int(row['method'])
                self.assertTrue(method.value==expected_method)


if __name__ == '__main__':
    unittest.main()
