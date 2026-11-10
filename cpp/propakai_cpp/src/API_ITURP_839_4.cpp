/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_839_4.h"
#include "ITURP_839_4.h"


PROPAKAI_API double P839_4_MeanAnnual0CIsothermHeight(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_839_4::MeanAnnual0CIsothermHeight(lat, lon);
	});
}

PROPAKAI_API double P839_4_MeanAnnualRainHeight(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_839_4::MeanAnnualRainHeight(lat, lon);
	});
}
