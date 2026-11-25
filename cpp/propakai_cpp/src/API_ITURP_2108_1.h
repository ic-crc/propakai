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
	P2108_1_WATER_SEA          = 1,
	P2108_1_OPEN_RURAL         = 2,
	P2108_1_SUBURBAN           = 3,
	P2108_1_URBAN_TREES_FOREST = 4,
	P2108_1_DENSE_URBAN        = 5
} P2108_1_ClutterCategory;

PROPAKAI_API double P2108_1_HeightGainTerminalCorrection(double f_GHz, double h_m, int clut, double R_m DEFARG(0.0), double ws_m DEFARG(27.0));
PROPAKAI_API double P2108_1_TerrestrialPathClutterLoss(double f_GHz, double distance_km, double location_percent);
PROPAKAI_API double P2108_1_EarthSpaceClutterLoss(double f_GHz, double theta_deg, double location_percent);

#ifdef __cplusplus
}
#endif

#undef DEFARG
