/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <vector>
#include "DigitalMap.h"


class ITURP_1510_1
{
public:
	/**
	 * @brief ITU-R P.1510-1, Annex 1, Section 1.
	 *
	 * Annual mean surface temperature at 2 m above the surface of the Earth (K).
	 *
	 * @param lat Latitude (degrees), with -90.0 <= lat <= 90.0.
	 * @param lon Longitude (degrees), with -180.0 <= lon <= 180.0.
	 * @return Annual mean surface temperature at 2 m above the surface of the Earth (K).
	 */
	static double AnnualMeanSurfaceTemperature(double lat, double lon);

	/**
	 * @brief ITU-R P.1510-1, Annex 1, Section 1.
	 *
	 * Monthly mean surface temperature at 2 m above the surface of the Earth (K).
	 *
	 * @param lat Latitude (degrees), with -90.0 <= lat <= 90.0.
	 * @param lon Longitude (degrees), with -180.0 <= lon <= 180.0.
	 * @param month Month (1 = Jan, ..., 12 = Dec).
	 * @return Monthly mean surface temperature at 2 m above the surface of the Earth (K).
	 */
	static double MonthlyMeanSurfaceTemperature(double lat, double lon, int month);

protected:
	static const DigitalMap s_TAnnual_map;
	static const std::vector<DigitalMap> s_TMonth_maps;

private:
	// Prevent instantiation
	ITURP_1510_1() = delete;
	ITURP_1510_1(const ITURP_1510_1&) = delete;
	ITURP_1510_1(ITURP_1510_1&&) = delete;
	ITURP_1510_1& operator=(const ITURP_1510_1&) = delete;
	ITURP_1510_1& operator=(ITURP_1510_1&&) = delete;
};
