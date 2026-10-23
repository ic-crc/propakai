# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Test module for p528_5_dso.py.
Uses .csv files from the "Data Table" folder from
https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.528-5-202109-I!!ZIP-E.zip
"""
import sys
from os.path import dirname, abspath, basename
from math import isclose
import unittest
from typing import cast
import pandas as pd
from propakai import p528_5_dso
sys.path.insert(0, dirname(abspath(__file__)))
import _test_utils as _tu


class Test_528_5_dso(unittest.TestCase):

    def test_basic_transmission_loss(self):
        csv_files = _tu.get_pathnames(_tu.ValidationFileGroup.P528_5_DATA_TABLES)

        for csv_file in csv_files:

            filename = basename(csv_file)
            mhz_index = filename.find(' MHz')
            f_mhz = float(filename[:mhz_index].replace(',', '').strip())

            lb_start = filename.find('Lb(') + 3
            lb_end = filename.find(')', lb_start)
            p_percent = float(filename[lb_start:lb_end].strip()) * 100.0

            csv_data = pd.read_csv(csv_file, skiprows=[0, 3], header=None)
            h2_m_list = list(csv_data.loc[0,2:])
            h1_m_list = list(csv_data.loc[1,2:])
            d_km_list = list(csv_data.loc[2:,0])
            lb_db_array = csv_data.loc[2:,2:].to_numpy()

            for i, d_km in enumerate(d_km_list):
                if i% 250 != 0:
                    continue # skip many distances, oterwise running all tests would take very long
                for j, (h1_m, h2_m) in enumerate(zip(h1_m_list, h2_m_list)):
                    lb_db = p528_5_dso.basic_transmission_loss(f_mhz=f_mhz, p_percent=p_percent,
                        d_km=d_km, hr1_mamsl=cast(float, h1_m), hr2_mamsl=cast(float, h2_m),
                        pol=p528_5_dso.Polarization.HORIZONTAL).a_db
                    self.assertTrue(isclose(lb_db, lb_db_array[i][j], abs_tol=5e-2))


if __name__ == '__main__':
    unittest.main()
