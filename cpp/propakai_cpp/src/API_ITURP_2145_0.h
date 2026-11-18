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

PROPAKAI_API double P2145_0_AUTO_CONSTANT();
PROPAKAI_API double P2145_0_SurfaceTotalPressure(double p_percent, double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_SurfaceTemperature(double p_percent, double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_SurfaceWaterVapourDensity(double p_percent, double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_IntegratedWaterVapourContent(double p_percent, double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_MeanSurfaceTotalPressure(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_MeanSurfaceTemperature(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_MeanSurfaceWaterVapourDensity(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_MeanIntegratedWaterVapourContent(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_StdDevSurfaceTotalPressure(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_StdDevSurfaceTemperature(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_StdDevSurfaceWaterVapourDensity(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_StdDevIntegratedWaterVapourContent(double lat, double lon, int month, double h_mamsl);
PROPAKAI_API double P2145_0_WeibullShapeParameter(double lat, double lon, double h_mamsl);
PROPAKAI_API double P2145_0_WeibullScaleParameter(double lat, double lon, double h_mamsl);

#ifdef __cplusplus
}
#endif
