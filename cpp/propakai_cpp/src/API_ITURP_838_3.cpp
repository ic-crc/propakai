/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_838_3.h"
#include "ITURP_838_3.h"


PROPAKAI_API double P838_3_RainAttenuation(double f_GHz, double R_mmhr, double theta_degrees, double tau_degrees)
{
	return ExecuteSafely([&]() {
		return ITURP_838_3::RainAttenuation(f_GHz, R_mmhr, theta_degrees, tau_degrees);
	});
}

PROPAKAI_API void P838_3_Coefficients(double f_GHz, double theta_degrees, double tau_degrees, double* outAlpha, double* outK)
{
	return ExecuteSafelyVoid([&]() {
		const auto [alpha, k] = ITURP_838_3::Coefficients(f_GHz, theta_degrees, tau_degrees);
		if (outAlpha) *outAlpha = alpha;
		if (outK) *outK = k;
	}, outAlpha, outK);
}
