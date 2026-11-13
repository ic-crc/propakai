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

PROPAKAI_API double P840_9_CloudOrFogAttenuation(double f_GHz, double T_K, double rhol_gm3);
PROPAKAI_API double P840_9_CloudLiquidWaterAttenuationCoefficient(double f_GHz, double T_K);
PROPAKAI_API double P840_9_SlantPathInstantaneousCloudAttenuation(double f_GHz, double theta_deg, double L_kgm2);
PROPAKAI_API double P840_9_SlantPathStatisticalCloudAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month = -1);
PROPAKAI_API double P840_9_LogNormalApproxToStatCloudAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon);
PROPAKAI_API double P840_9_IntegratedCloudLiquidWaterContent(double p_percent, double lat, double lon, int month = -1);
PROPAKAI_API double P840_9_MeanIntegratedCloudLiquidWaterContent(double lat, double lon, int month = -1);
PROPAKAI_API double P840_9_StdDevIntegratedCloudLiquidWaterContent(double lat, double lon, int month = -1);

#ifdef __cplusplus
}
#endif
