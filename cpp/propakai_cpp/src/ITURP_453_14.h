/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include "DigitalMap.h"


class ITURP_453_14
{
public:
	/**
	 * @brief Gets the median value of the wet term of the surface refractivity exceeded for the
	 *        average year (ppm).
	 *
	 * ITU-R P.453-14, Annex 1, Section 2.2.
	 *
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 *
	 * @return The median value of the wet term of the surface refractivity exceeded for the
	 *         average year (ppm).
	 */
	static double MedianAnnualNWet(double lat, double lon);

protected:
	static const DigitalMap s_NWET_Annual_50_map;

private:
	// Prevent instantiation
	ITURP_453_14() = delete;
	ITURP_453_14(const ITURP_453_14&) = delete;
	ITURP_453_14(ITURP_453_14&&) = delete;
	ITURP_453_14& operator=(const ITURP_453_14&) = delete;
	ITURP_453_14& operator=(ITURP_453_14&&) = delete;
};
