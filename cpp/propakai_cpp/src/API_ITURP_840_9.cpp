/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_840_9.h"
#include "ITURP_840_9.h"


PROPAKAI_API double P840_9_CloudOrFogAttenuation(double f_GHz, double T_K, double rhol_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::CloudOrFogAttenuation(f_GHz, T_K, rhol_gm3);
	});
}

PROPAKAI_API double P840_9_CloudLiquidWaterAttenuationCoefficient(double f_GHz, double T_K)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::CloudLiquidWaterAttenuationCoefficient(f_GHz, T_K);
	});
}

PROPAKAI_API double P840_9_SlantPathInstantaneousCloudAttenuation(double f_GHz, double theta_deg, double L_kgm2)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::SlantPathInstantaneousCloudAttenuation(f_GHz, theta_deg, L_kgm2);
	});
}

PROPAKAI_API double P840_9_SlantPathStatisticalCloudAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::SlantPathStatisticalCloudAttenuation(f_GHz, theta_deg, p_percent, lat, lon, month);
	});
}

PROPAKAI_API double P840_9_LogNormalApproxToStatCloudAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::LogNormalApproxToStatCloudAttenuation(f_GHz, theta_deg, p_percent, lat, lon);
	});
}

PROPAKAI_API double P840_9_IntegratedCloudLiquidWaterContent(double p_percent, double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::IntegratedCloudLiquidWaterContent(p_percent, lat, lon, month);
	});
}

PROPAKAI_API double P840_9_MeanIntegratedCloudLiquidWaterContent(double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::MeanIntegratedCloudLiquidWaterContent(lat, lon, month);
	});
}

PROPAKAI_API double P840_9_StdDevIntegratedCloudLiquidWaterContent(double lat, double lon, int month)
{
	return ExecuteSafely([&]() {
		return ITURP_840_9::StdDevIntegratedCloudLiquidWaterContent(lat, lon, month);
	});
}
