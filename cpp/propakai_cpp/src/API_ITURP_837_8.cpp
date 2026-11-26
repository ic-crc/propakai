/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_837_8.h"
#include "ITURP_837_8.h"


PROPAKAI_API double P837_8_AnnualRainfallRate001(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_837_8::AnnualRainfallRate001(lat, lon);
	});
}

PROPAKAI_API double P837_8_TotalMonthlyMeanRainfall(double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_837_8::TotalMonthlyMeanRainfall(lat, lon, month);
	});
}

PROPAKAI_API void P837_8_AnnualRainfallRate(double p_percent, double lat, double lon, double* RpAnnual_mmhr, double* P0Annual_percent)
{
	return ExecuteSafelyVoid([&]() {
		const auto [Rp, P0] = ITURP_837_8::AnnualRainfallRate(p_percent, lat, lon);
		if (RpAnnual_mmhr) *RpAnnual_mmhr = Rp;
		if (P0Annual_percent) *P0Annual_percent = P0;
	}, RpAnnual_mmhr, P0Annual_percent);
}

PROPAKAI_API double P837_8_AnnualProbabilityOfRain(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_837_8::AnnualProbabilityOfRain(lat, lon);
	});
}

PROPAKAI_API void P837_8_MonthlyRainfallRate(double p_percent, double lat, double lon, int month, double* RpMonthly_mmhr, double* P0Monthly_percent)
{
	return ExecuteSafelyVoid([&]() {
		const auto [Rp, P0] = ITURP_837_8::MonthlyRainfallRate(p_percent, lat, lon, month);
		if (RpMonthly_mmhr) *RpMonthly_mmhr = Rp;
		if (P0Monthly_percent) *P0Monthly_percent = P0;
	}, RpMonthly_mmhr, P0Monthly_percent);
}

PROPAKAI_API double P837_8_MonthlyProbabilityOfRain(double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_837_8::MonthlyProbabilityOfRain(lat, lon, month);
	});
}
