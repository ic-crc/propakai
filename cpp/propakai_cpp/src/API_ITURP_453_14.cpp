/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_453_14.h"
#include "ITURP_453_14.h"


PROPAKAI_API double P453_14_MedianAnnualNWet(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_453_14::MedianAnnualNWet(lat, lon);
	});
}
