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

PROPAKAI_API double P837_8_AnnualRainfallRate001(double lat, double lon);
PROPAKAI_API double P837_8_TotalMonthlyMeanRainfall(double lat, double lon, int month);
PROPAKAI_API void   P837_8_AnnualRainfallRate(double p_percent, double lat, double lon, double* RpAnnual_mmhr, double* P0Annual_percent);
PROPAKAI_API double P837_8_AnnualProbabilityOfRain(double lat, double lon);
PROPAKAI_API void   P837_8_MonthlyRainfallRate(double p_percent, double lat, double lon, int month, double* RpMonthly_mmhr, double* P0Monthly_percent);
PROPAKAI_API double P837_8_MonthlyProbabilityOfRain(double lat, double lon, int month);

#ifdef __cplusplus
}
#endif
