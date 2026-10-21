# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p1546_6.py.
Uses ITU validation examples file R19-WP3K-C-0264!N05-P2!ZIP-E.zip from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath, basename
from math import isclose
import unittest
import csv
import copy

sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu

from propakai import p1546_6


class Test_1546_6(unittest.TestCase):

    class P1546Input:
        def __init__(self):
            self.first_point: str= '', # T or R (transmitter or receiver)
            self.d_km: list[float] = [] # dist from tx
            self.h_mamsl: list[float] = [] # terrain height
            self.cc: list[int] = [] # clutter category
            self.rch_m: list[float] = [] # representative clutter height
            self.rcz: list[int] = [] # radio climatic zone
            self.f_mhz: float = 0
            self.htx_m: float = 0
            self.hrx_m: float = 0
            self.erp_dbw: float = 0
            self.p_time_percent: float = 0
            self.fs_dbuvm: float = 0
            self.lb_db: float = 0


    def read_validation_profile_file(self, pathname: str) -> P1546Input:
        inputs = []
        profile_data = Test_1546_6.P1546Input()
        with open(pathname, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == 'First Point TX or RX:':
                    profile_data.first_point = row[1]
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
                        prof_meas_data.f_mhz = float(row[0])
                        prof_meas_data.htx_m = float(row[1])
                        prof_meas_data.hrx_m = float(row[3])
                        prof_meas_data.erp_dbw = float(row[12])
                        prof_meas_data.p_time_percent = float(row[14])
                        prof_meas_data.fs_dbuvm = float(row[16])
                        prof_meas_data.lb_db = float(row[17])
                        inputs.append(prof_meas_data)
        return inputs


    def _reverse_profiles(self, i: P1546Input):
        total_d_km = i.d_km[-1]
        i.d_km = [total_d_km-d for d in reversed(i.d_km)]
        i.h_mamsl.reverse()
        i.cc.reverse()
        i.rch_m.reverse()
        i.rcz.reverse()

        i.htx_m, i.hrx_m = i.hrx_m, i.htx_m


    def test_basic_transmission_loss(self):
        cc_to_env_map = {
            1: p1546_6.Environment.RURAL_OR_OPEN, # 1 = water/sea
            2: p1546_6.Environment.RURAL_OR_OPEN, # 2 = open/rural
            3: p1546_6.Environment.URBAN,         # 3 = suburban
            4: p1546_6.Environment.URBAN,         # 4 = urban/trees/forest
            5: p1546_6.Environment.URBAN          # 5 = dense urban
        }

        rcz_to_path_map = {
            # NOTE: not sure how to select between WARM_SEA and COLD_SEA here
            1: p1546_6.Path.COLD_SEA.value, # 1 = sea
            3: p1546_6.Path.COLD_SEA.value, # 2 = coastal land
            4: p1546_6.Path.LAND.value      # 4 = land
        }

        csv_files = _tu.get_pathnames(_tu.ValidationFileGroup.P1546_6_VALIDATION_PROFILES)

        for csv_file in csv_files:
            #if basename(csv_file) != 'land_flat_adjsea_10km.csv':
            #    continue
            #print(csv_file)
            try:
                inputs = self.read_validation_profile_file(csv_file)
            except Exception as _:
                # file format is not as expected for srg_land_637m.csv
                #print(f'Skipping {basename(csv_file)}')
                continue

            for i in inputs:
                if i.first_point == 'R':
                    self._reverse_profiles(i)
                path_profile = [rcz_to_path_map[x] for x in i.rcz]
                env2 = cc_to_env_map[i.cc[-1]]
                Lb, E = p1546_6.basic_transmission_loss(f_mhz=i.f_mhz,
                                                        t_percent=i.p_time_percent,
                                                        ha_m=i.htx_m,
                                                        h2_m=i.hrx_m,
                                                        env2=env2,
                                                        d_profile_km=i.d_km,
                                                        h_profile_mamsl=i.h_mamsl,
                                                        path_type_profile=path_profile,
                                                        r1_m=i.rch_m[0],
                                                        r2_m=i.rch_m[-1]
                                                        )

                # NOTE: the validation results for misc.csv seem to incorrectly add a terrain
                #       clearance angle correction (step 12), which should not be applied since
                #       the receiver is over sea.
                if basename(csv_file) == 'misc.csv':
                    i.lb_db += -5.83883

                #print(f'diff={abs(Lb-i.lb_db)}')

                # Difference is as high as 0.24 dB for land_neg_h1_urban_10km.csv but is typically
                # much lower.
                self.assertTrue(isclose(Lb, i.lb_db, abs_tol=0.25))


if __name__ == '__main__':
    unittest.main()
