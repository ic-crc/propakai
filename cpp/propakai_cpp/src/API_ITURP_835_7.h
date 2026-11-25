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
	P835_7_ITU_R           = 1,
	P835_7_SEASONAL_SUMMER = 2,
	P835_7_SEASONAL_WINTER = 3
} P835_7_ReferenceAtmosphere;

PROPAKAI_API double P835_7_Temperature(double z_km, int atm DEFARG(P835_7_ITU_R), double lat DEFARG(45.0));
PROPAKAI_API double P835_7_Pressure(double z_km, int atm DEFARG(P835_7_ITU_R), double lat DEFARG(45.0));
PROPAKAI_API double P835_7_WaterVapourDensity(double z_km, int atm DEFARG(P835_7_ITU_R), double lat DEFARG(45.0));

#ifdef __cplusplus
}
#endif

#undef DEFARG
