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
	P1812_8_COASTAL_LAND = 3,
	P1812_8_INLAND       = 4,
	P1812_8_SEA          = 1
} P1812_8_RadioClimaticZone;

typedef enum {
	P1812_8_WATER_SEA           = 1,
	P1812_8_OPEN_RURAL          = 2,
	P1812_8_SUBURBAN            = 3,
	P1812_8_URBAN_TREES_FOREST  = 4,
	P1812_8_DENSE_URBAN         = 5
} P1812_8_ClutterCategory;

PROPAKAI_API double P1812_8_BasicTransmissionloss(
	double f_GHz, double p_percent, double pL_percent, double latt, double lont, double latr, double lonr,
	double htg_m, double hrg_m, bool vpol, unsigned int n, const double* d_km, const double* h_mamsl,
	const int* cc DEFARG(nullptr), const double* rch_m DEFARG(nullptr), const double* sh_mamsl DEFARG(nullptr),
	const int* rcz DEFARG(nullptr), double dct_km DEFARG(PROPAKAI_AUTO), double dcr_km DEFARG(PROPAKAI_AUTO),
	double deltaN DEFARG(PROPAKAI_AUTO), double N0 DEFARG(PROPAKAI_AUTO), double wa_m DEFARG(100.0));

PROPAKAI_API double P1812_8_FieldStrength(double f_GHz, double Lb_dB);

#ifdef __cplusplus
}
#endif

#undef DEFARG
