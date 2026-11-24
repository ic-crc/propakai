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

PROPAKAI_API double P1511_3_TopographicHeight(double lat, double lon);
PROPAKAI_API double P1511_3_GeocentricEarthRadius(double geodeticLat);
PROPAKAI_API double P1511_3_GeodeticToGeocentricLatitude(double geodeticLat);
PROPAKAI_API double P1511_3_GeocentricToGeodeticLatitude(double geocentricLat);
PROPAKAI_API double P1511_3_GeoidUndulation(double lat, double lon);
PROPAKAI_API void   P1511_3_GeodeticToAer(double latG, double lonG, double hG_km, double latS, double lonS, double hS_km, double* outAzimuth_deg, double* outElevation_deg, double* outSlantRange_km);

#ifdef __cplusplus
}
#endif
