/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_2109_2.h"
#include "ITURP_2109_2.h"


PROPAKAI_API double P2109_2_BuildingEntryLoss(double f_GHz, double probability_percent,
                                              double elevAngle_degrees, bool thermally_efficient)
{
	return ITURP_2109_2::BuildingEntryLoss(f_GHz, probability_percent, elevAngle_degrees, thermally_efficient);
}
