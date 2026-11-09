/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_1510_1.h"
#include "ITURP_1510_1.h"


PROPAKAI_API double P1510_1_AnnualMeanSurfaceTemperature(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_1510_1::AnnualMeanSurfaceTemperature(lat, lon);
	});
}

PROPAKAI_API double P1510_1_MonthlyMeanSurfaceTemperature(double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_1510_1::MonthlyMeanSurfaceTemperature(lat, lon, month);
	});
}
