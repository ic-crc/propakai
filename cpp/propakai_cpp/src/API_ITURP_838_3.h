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

PROPAKAI_API double P838_3_RainAttenuation(double f_GHz, double R_mmhr, double theta_degrees, double tau_degrees);
PROPAKAI_API void   P838_3_Coefficients(double f_GHz, double theta_degrees, double tau_degrees, double* outAlpha, double* outK);

#ifdef __cplusplus
}
#endif
