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

PROPAKAI_API double P2109_2_BuildingEntryLoss(
	double f_GHz, double probability_percent, double elevAngle_degrees, bool thermally_efficient);

#ifdef __cplusplus
}
#endif
