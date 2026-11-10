/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include "DigitalMap.h"


class ITURP_839_4
{
public:
	/**
	 * @brief Gets the mean annual 0°C isotherm height (km above mean sea level).
	 *
	 * ITU-R P.839-4.
	 *
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 *
	 * @return The mean annual 0°C isotherm height (km above mean sea level).
	 */
	static double MeanAnnual0CIsothermHeight(double lat, double lon);

	/**
	 * @brief Gets the mean annual rain height (km above mean sea level).
	 *
	 * ITU-R P.839-4.
	 *
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 *
	 * @return The mean annual rain height (km above mean sea level).
	 */
	static double MeanAnnualRainHeight(double lat, double lon);

protected:
	static const DigitalMap s_h0_map;

private:
	// Prevent instantiation
	ITURP_839_4() = delete;
	ITURP_839_4(const ITURP_839_4&) = delete;
	ITURP_839_4(ITURP_839_4&&) = delete;
	ITURP_839_4& operator=(const ITURP_839_4&) = delete;
	ITURP_839_4& operator=(ITURP_839_4&&) = delete;
};
