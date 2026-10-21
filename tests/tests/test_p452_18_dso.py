# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p452_18_dso.py.
Uses ITU validation examples files from
https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx (Validation Examples tab)
"""
import sys
from os.path import dirname, abspath, basename
from math import isclose
import unittest
import csv

sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu

from propakai import p452_18_dso


class Test_452_18_dso(unittest.TestCase):

    class ProfileSet:
        def __init__(self):
            self.d_km: list[float] = [] # dist from tx
            self.h_mamsl: list[float] = [] # terrain height
            self.rch_m: list[float] = [] # representative clutter height
            self.rcz: list[int] = [] # radio climatic zone


    def read_profile_csv_file(self, csv_file: str) -> ProfileSet:
        profile_data = Test_452_18_dso.ProfileSet()
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            _header = next(reader)  # Skip header row
            for row in reader:
                profile_data.d_km.append(float(row[0]))
                profile_data.h_mamsl.append(float(row[1]))
                profile_data.rch_m.append(float(row[2]))
                profile_data.rcz.append(int(row[4]))
        # Note: Radio climatic zone IDs in profile files do not correspond to those
        #       used by p452_18_dso. Need to apply some mapping.
        mapping = {1: 3, 2: 4, 3: 1}
        converted_rcz = [mapping[x] for x in profile_data.rcz]
        profile_data.rcz = converted_rcz
        return profile_data


    class Result:
        def __init__(self):
            self.profile_filename: str
            self.f_ghz: float
            self.p_percent: float
            self.latt: float
            self.lont: float
            self.latr: float
            self.lonr: float
            self.htg_m: float
            self.hrg_m: float
            self.gt_dbi: float
            self.gr_dbi: float
            self.vpol: bool
            self.dct_km: float
            self.dcr_km: float
            self.delta_n: float
            self.n0: float
            self.p_hpa: float
            self.t_c: float
            self.lb_db: float


    def read_result_csv_file(self, csv_file: str) -> list[Result]:
        results = []
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                result = Test_452_18_dso.Result()
                result.profile_filename = row['profile']
                # Note: fix for the one result file which contains the wrong profile filename
                if basename(csv_file) == 'test_result_b2iseac_land_eqdist_no_clutter.csv':
                    result.profile_filename = 'test_profile_b2iseac_land_eqdist_no_clutter.csv'
                result.f_ghz = float(row['f (GHz)'])
                result.p_percent = float(row['p (%)'])
                result.latt = float(row['phit_n (deg)'])
                result.lont = float(row['phit_e (deg)'])
                result.latr = float(row['phir_n (deg)'])
                result.lonr = float(row['phir_e (deg)'])
                result.htg_m = float(row['htg (m)'])
                result.hrg_m = float(row['hrg (m)'])
                result.gt_dbi = float(row['Gt (dBi)'])
                result.gr_dbi = float(row['Gr (dBi)'])
                result.vpol = bool(int(row['pol (1-h/2-v)'])==2)
                result.dct_km = float(row['dct (km)'])
                result.dcr_km = float(row['dcr (km)'])
                result.delta_n = float(row['DN'])
                result.n0 = float(row['N0'])
                result.p_hpa = float(row['press (hPa)'])
                result.t_c = float(row['temp (deg C)'])
                result.lb_db = float(row['Lb'])
                results.append(result)
        return results


    def read_csv_files(self, csv_files: list[str]):
        profiles = {}
        results = []
        for csv_file in csv_files:
            filename = basename(csv_file)
            if '_profile_' in filename:
                profiles[filename] = self.read_profile_csv_file(csv_file)
            elif '_result_' in filename:
                results.extend(self.read_result_csv_file(csv_file))
        return profiles, results


    def test_basic_transmission_loss(self):
        csv_files = _tu.get_pathnames(_tu.ValidationFileGroup.P452_18_VALIDATION_PROFILES)
        profiles, results = self.read_csv_files(csv_files)

        for r in results:
            params = {
                'f_ghz': r.f_ghz,
                'p_percent': r.p_percent,
                'worst_month': False,
                'latt': r.latt,
                'lont': r.lont,
                'latr': r.latr,
                'lonr': r.lonr,
                'htg_m': r.htg_m,
                'hrg_m': r.hrg_m,
                'gt_dbi': r.gt_dbi,
                'gr_dbi': r.gr_dbi,
                'vpol': r.vpol,
                'd_km': profiles[r.profile_filename].d_km,
                'h_mamsl': profiles[r.profile_filename].h_mamsl,
                'cc': None,
                'rch_m': profiles[r.profile_filename].rch_m,
                'rcz': profiles[r.profile_filename].rcz,
                'dct_km': r.dct_km,
                'dcr_km': r.dcr_km,
                'delta_n': r.delta_n,
                'n0': r.n0,
                'p_hpa': r.p_hpa,
                't_c': r.t_c
            }

            lb_db = p452_18_dso.clear_air_basic_transmission_loss(**params)
            self.assertTrue(isclose(lb_db, r.lb_db))

            # test having clear_air_basic_transmission_loss() compute DN and N0 values itself
            auto_dn_n0_params = {**params, 'delta_n': None, 'n0': None}
            lb_db = p452_18_dso.clear_air_basic_transmission_loss(**auto_dn_n0_params)
            self.assertTrue(isclose(lb_db, r.lb_db))


if __name__ == '__main__':
    unittest.main()
