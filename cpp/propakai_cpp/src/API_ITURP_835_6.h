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
extern "C" {
#endif

typedef enum {
	P835_6_MEAN_ANNUAL_GLOBAL   = 1,
	P835_6_LOW_LATITUDE         = 2,
	P835_6_MID_LATITUDE_SUMMER  = 3,
	P835_6_MID_LATITUDE_WINTER  = 4,
	P835_6_HIGH_LATITUDE_SUMMER = 5,
	P835_6_HIGH_LATITUDE_WINTER = 6
} P835_6_ReferenceAtmosphere;

#ifdef __cplusplus
}
#endif
