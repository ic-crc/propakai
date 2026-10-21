# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p2001_6.py.

Compares local digital map values from from those from the ITU Geodata Catalog:
https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.1510-1-201706
"""
import sys
from os.path import dirname, abspath, basename
from math import isclose
import unittest
import csv

sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu

from propakai import p2001_6
from propakai.geo_catalog import gc_p2001_6


class Test_P2001_6(unittest.TestCase):

    def test_digital_maps_against_geocatalog(self):
        locations = [(0,0), (45,-75), (-45,-75), (45,75), (-45,75)]
        locations += [(0.1,0.9), (45.9,-75.1), (-45.1,-75.9), (45.9,75.1), (-45.1,75.9)]
        for location in locations:
            lat = location[0]
            lon = location[1]

            delta_N = p2001_6._digital_map_value(p2001_6._MapId.DN_MEDIAN, lat, lon)
            N_d1km50 = p2001_6._N_d1km50(lat, lon)
            expected_val = gc_p2001_6.median_avg_refractivity_gradient_1km(lat, lon)
            self.assertTrue(isclose(-delta_N, expected_val))
            self.assertTrue(isclose(N_d1km50, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.DN_SUPSLOPE, lat, lon)
            expected_val = gc_p2001_6.supslope_avg_refractivity_gradient_1km(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.DN_SUBSLOPE, lat, lon)
            expected_val = gc_p2001_6.subslope_avg_refractivity_gradient_1km(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.DNDZ_01, lat, lon)
            expected_val = gc_p2001_6.refractivity_gradient_65m(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            # NOTE: As of Sept. 2026, there is a known bug in the ITU-R Geospatial Catalog API:
            # `Esarain_Pr6` returns the value of `Esarain_Beta` and vice-versa.
            val = p2001_6._digital_map_value(p2001_6._MapId.ESARAIN_PR6_V5, lat, lon)
            #expected_val = gc_p2001_6.probability_of_rain_6h(lat, lon)
            expected_val = gc_p2001_6.beta_rain_ratio(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.ESARAIN_MT_V5, lat, lon)
            expected_val = gc_p2001_6.annual_rainfall_accumulation(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            # NOTE: As of Sept. 2026, there is a known bug in the ITU-R Geospatial Catalog API:
            # `Esarain_Pr6` returns the value of `Esarain_Beta` and vice-versa.
            val = p2001_6._digital_map_value(p2001_6._MapId.ESARAIN_BETA_V5, lat, lon)
            #expected_val = gc_p2001_6.beta_rain_ratio(lat, lon)
            expected_val = gc_p2001_6.probability_of_rain_6h(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.H0, lat, lon)
            expected_val = gc_p2001_6.mean_annual_0c_isotherm_height(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.SURFWV_50_FIXED, lat, lon)
            expected_val = gc_p2001_6.surface_water_vapour_density(lat, lon)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.FOES50, lat, lon)
            expected_val = gc_p2001_6.sporadic_e_critical_frequency(lat, lon, 50)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.FOES10, lat, lon)
            expected_val = gc_p2001_6.sporadic_e_critical_frequency(lat, lon, 10)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.FOES01, lat, lon)
            expected_val = gc_p2001_6.sporadic_e_critical_frequency(lat, lon, 1)
            self.assertTrue(isclose(val, expected_val))

            val = p2001_6._digital_map_value(p2001_6._MapId.FOES0_1, lat, lon)
            expected_val = gc_p2001_6.sporadic_e_critical_frequency(lat, lon, 0.1)
            self.assertTrue(isclose(val, expected_val))

            val  = p2001_6._digital_map_value(p2001_6._MapId.TROPOCLIM, lat, lon)
            expected_val = gc_p2001_6.climatic_zone(lat, lon)
            self.assertTrue(isclose(val, expected_val))


    class P2001Profiles:
        def __init__(self):
            self.tx_lat: float = 0
            self.tx_lon: float = 0
            self.rx_lat: float = 0
            self.rx_lon: float = 0
            self.d_km: list[float] = [] # dist from tx
            self.h_mamsl: list[float] = [] # terrain height
            self.z: list[int] = [] # radio climatic zone


    def read_profile_file(self, pathname: str) -> P2001Profiles:
        profile_data = Test_P2001_6.P2001Profiles()
        with open(pathname, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == 'TxCoordN':
                    profile_data.tx_lat = float(row[1])
                if row[0] == 'TxCoordE':
                    profile_data.tx_lon = float(row[1])
                if row[0] == 'RxCoordN':
                    profile_data.rx_lat = float(row[1])
                if row[0] == 'RxCoordE':
                    profile_data.rx_lon = float(row[1])
                if row[0] == 'Points':
                    for row in reader:
                        profile_data.d_km.append(float(row[0]))
                        profile_data.h_mamsl.append(float(row[1]))
                        profile_data.z.append(int(row[2]))
        return profile_data


    def test_basic_transmission_loss(self):

        csv_files = _tu.get_pathnames(_tu.ValidationFileGroup.P2001_6_VALIDATION_PROFILES)

        # read profile files
        profiles = {}
        for csv_file in csv_files:
            filename = basename(csv_file)
            if '_profile' in filename:
                profile = self.read_profile_file(csv_file)
                if 'b2iseac' in filename:
                    profiles['b2iseac'] = profile
                elif 'prof4' in filename:
                    profiles['prof4'] = profile

        # read result files
        for csv_file in csv_files:
            filename = basename(csv_file)
            if '_results' in filename:
                profile = None
                if 'b2iseac' in filename:
                    profile = profiles['b2iseac']
                elif 'prof4' in filename:
                    profile = profiles['prof4']

                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        f_ghz = float(row['GHz'])
                        tpc_percent = float(row['Tpc'])
                        htg_m = float(row['Htg'])
                        hrg_m = float(row['Hrg'])
                        gt_dbi = float(row['Grt'])
                        gr_dbi = float(row['Grx'])
                        vpol = bool(row['FlagVp'])
                        expected_Lb = float(row['Lb'])

                        Lb, Lbm1, Lbm2, Lbm3, Lbm4 = \
                            p2001_6.basic_transmission_loss(f_ghz, tpc_percent, profile.tx_lat,
                                profile.tx_lon, profile.rx_lat, profile.rx_lon, htg_m, hrg_m,
                                gt_dbi, gr_dbi, vpol, profile.d_km, profile.h_mamsl, profile.z)

                        expected_Lb = float(row['Lb'])

                        self.assertTrue(isclose(Lb, expected_Lb))


if __name__ == '__main__':
    unittest.main()
