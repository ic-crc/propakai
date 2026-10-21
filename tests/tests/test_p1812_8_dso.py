# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p1812_8_dso.py.
Uses ITU validation examples file R19-WP3K-C-0335!N02-P2!ZIP-E.zip from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath
from math import isclose
import unittest
import csv
import copy
import operator

sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu

from propakai import p1812_8_dso


class Test_1812_8_dso(unittest.TestCase):

    class P1812Input:
        def __init__(self):
            self.tx_lat: float = 0
            self.tx_lon: float = 0
            self.rx_lat: float = 0
            self.rx_lon: float = 0
            self.dn: float = 0
            self.n0: float = 0
            self.d_km: list[float] = [] # dist from tx
            self.h_mamsl: list[float] = [] # terrain height
            self.cc: list[int] = [] # clutter category
            self.rch_m: list[float] = [] # representative clutter height
            self.rcz: list[int] = [] # radio climatic zone
            self.f_ghz: float = 0
            self.htx_m: float = 0
            self.hrx_m: float = 0
            self.pol: int = 0
            self.erp_dbw: float = 0
            self.p_time_percent: float = 0
            self.fs_dbuvm: float = 0
            self.lb_db: float = 0


    def read_validation_profile_file(self, pathname: str) -> P1812Input:
        inputs = []
        profile_data = Test_1812_8_dso.P1812Input()
        with open(pathname, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == 'Tx LAT:':
                    profile_data.tx_lat = float(row[1])
                if row[0] == 'Tx LON:':
                    profile_data.tx_lon = float(row[1])
                if row[0] == 'Rx LAT:':
                    profile_data.rx_lat = float(row[1])
                if row[0] == 'Rx LON:':
                    profile_data.rx_lon = float(row[1])
                if row[0] == 'Average annual values dN (N-units/km):':
                    profile_data.dn = float(row[1])
                if row[0] == 'Average annual sea-level surface refractivity No (N-units):':
                    profile_data.n0 = float(row[1])
                if row[0] == '{Begin of Profile}':
                    _skipped_row = next(reader)
                    for row in reader:
                        if row[0] == '{End of Profile}':
                            break
                        profile_data.d_km.append(float(row[0]))
                        profile_data.h_mamsl.append(float(row[1]))
                        profile_data.cc.append(int(row[2]))
                        profile_data.rch_m.append(float(row[3]))
                        profile_data.rcz.append(int(row[4]))
                if row[0] == '{Begin of Measurements}':
                    for row in reader:
                        if row[0] == '{End of Measurements}':
                            break
                        prof_meas_data = copy.deepcopy(profile_data)
                        prof_meas_data.f_ghz = float(row[0])/1000.0
                        prof_meas_data.htx_m = float(row[1])
                        prof_meas_data.hrx_m = float(row[3])
                        prof_meas_data.pol = int(row[4])
                        prof_meas_data.erp_dbw = float(row[12])
                        prof_meas_data.p_time_percent = float(row[14])
                        prof_meas_data.fs_dbuvm = float(row[16])
                        prof_meas_data.lb_db = float(row[17])
                        inputs.append(prof_meas_data)
        return inputs


    def is_using_default_representative_heights(self, i: P1812Input) -> bool:
        for clutter_cat, repr_height in zip(i.cc, i.rch_m):
            if clutter_cat==1 and repr_height != 0:
                return False
            if clutter_cat==2 and repr_height != 0:
                return False
            if clutter_cat==3 and repr_height != 10:
                return False
            if clutter_cat==4 and repr_height != 15:
                return False
            if clutter_cat==5 and repr_height != 20:
                return False
        return True


    def test_basic_transmission_loss(self):
        csv_files = _tu.get_pathnames(_tu.ValidationFileGroup.P1812_8_VALIDATION_PROFILES)

        for csv_file in csv_files:
            inputs = self.read_validation_profile_file(csv_file)
            for i in inputs:
                params = {
                    'f_ghz': i.f_ghz,
                    'p_percent': i.p_time_percent,
                    'pl_percent': 50.0,
                    'latt': i.tx_lat,
                    'lont': i.tx_lon,
                    'latr': i.rx_lat,
                    'lonr': i.rx_lon,
                    'htg_m': i.htx_m,
                    'hrg_m': i.hrx_m,
                    'vpol': i.pol==2,
                    'd_km': i.d_km,
                    'h_mamsl': i.h_mamsl,
                    'cc': i.cc,
                    'rch_m': i.rch_m,
                    'sh_mamsl': None,
                    'rcz': i.rcz,
                    'dct_km': 500.0,
                    'dcr_km': 500.0,
                    'delta_n': i.dn,
                    'n0': i.n0
                }

                # test using representative clutter heights
                using_rch_params = {**params, 'cc': None}
                lb_db = p1812_8_dso.basic_transmission_loss(**using_rch_params)
                self.assertTrue(isclose(lb_db, i.lb_db))

                # test using clutter categories (when possible)
                if self.is_using_default_representative_heights(i) is True:
                    using_cc_params = {**params, 'rch_m': None}
                    lb_db = p1812_8_dso.basic_transmission_loss(**using_cc_params)
                    self.assertTrue(isclose(lb_db, i.lb_db))

                # test using surface height data
                sh_mamsl = list(map(operator.add, i.h_mamsl, i.rch_m))
                using_sh_params = {**params, 'cc': None, 'rch_m': None, 'sh_mamsl': sh_mamsl}
                lb_db = p1812_8_dso.basic_transmission_loss(**using_sh_params)
                self.assertTrue(isclose(lb_db, i.lb_db))

                erp_dbkw = i.erp_dbw - 30.0
                fs_1kw_erp_dbuvm = p1812_8_dso.field_strength(i.f_ghz, lb_db)
                fs_dbuvm = fs_1kw_erp_dbuvm + erp_dbkw
                self.assertTrue(isclose(fs_dbuvm, i.fs_dbuvm, rel_tol=1e-8))


if __name__ == '__main__':
    unittest.main()
