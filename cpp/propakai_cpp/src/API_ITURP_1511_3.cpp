/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_1511_3.h"
#include "ITURP_1511_3.h"


PROPAKAI_API double P1511_3_TopographicHeight(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::TopographicHeight(lat, lon);
	});
}

PROPAKAI_API double P1511_3_GeocentricEarthRadius(double geodeticLat)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::GeocentricEarthRadius(geodeticLat);
	});
}

PROPAKAI_API double P1511_3_GeodeticToGeocentricLatitude(double geodeticLat)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::GeodeticToGeocentricLatitude(geodeticLat);
	});
}

PROPAKAI_API double P1511_3_GeocentricToGeodeticLatitude(double geocentricLat)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::GeocentricToGeodeticLatitude(geocentricLat);
	});
}

PROPAKAI_API double P1511_3_GeoidUndulation(double lat, double lon)
{
	return ExecuteSafely([&]() {
		return ITURP_1511_3::GeoidUndulation(lat, lon);
	});
}

PROPAKAI_API void P1511_3_GeodeticToAer(double latG, double lonG, double hG_km, double latS, double lonS, double hS_km,
                                        double* outAzimuth_deg, double* outElevation_deg, double* outSlantRange_km)
{
	return ExecuteSafelyVoid([&]() {
		const auto [alpha_deg, v_deg, R_km] = ITURP_1511_3::GeodeticToAer(latG, lonG, hG_km, latS, lonS, hS_km);
		if (outAzimuth_deg)   *outAzimuth_deg = alpha_deg;
		if (outElevation_deg) *outElevation_deg = v_deg;
		if (outSlantRange_km) *outSlantRange_km = R_km;
	}, outAzimuth_deg, outElevation_deg, outSlantRange_km);
}