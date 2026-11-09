/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_1511_3.h"
#include "ITURP_1511_3.h"


PROPAKAI_API double P1511_3_TopographicHeight(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::TopographicHeight(lat, lon);
	});
}

PROPAKAI_API double P1511_3_GeoidUndulation(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::GeoidUndulation(lat, lon);
	});
}
