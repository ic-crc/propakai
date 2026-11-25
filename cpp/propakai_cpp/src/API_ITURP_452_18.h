/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once

#include "API_PropaKai.h"

#ifdef __cplusplus
	#define DEFARG(val) = val
#else
	#define DEFARG(val)
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
	P452_18_COASTAL_LAND = 3,
	P452_18_INLAND       = 4,
	P452_18_SEA          = 1
} P452_18_RadioClimaticZone;

typedef enum {
	P452_18_WATER_SEA           = 1,
	P452_18_OPEN_RURAL          = 2,
	P452_18_SUBURBAN            = 3,
	P452_18_URBAN_TREES_FOREST  = 4,
	P452_18_DENSE_URBAN         = 5
} P452_18_ClutterCategory;

PROPAKAI_API double P452_18_ClearAirBasicTransmissionLoss(
	double f_GHz, double p_percent, bool worstMonth, double latt, double lont, double latr, double lonr,
	double htg_m, double hrg_m, double Gt_dBi, double Gr_dBi, bool vpol, unsigned int n, const double* d_km,
	const double* h_mamsl, const int* cc DEFARG(nullptr), const double* rch_m DEFARG(nullptr), const int* rcz DEFARG(nullptr),
	double dct_km DEFARG(PROPAKAI_AUTO), double dcr_km DEFARG(PROPAKAI_AUTO), double P_hPa DEFARG(1013.25),
	double T_C DEFARG(15.0), double deltaN DEFARG(PROPAKAI_AUTO), double N0 DEFARG(PROPAKAI_AUTO));

#ifdef __cplusplus
}
#endif

#undef DEFARG
