/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include "DigitalMap.h"


class ITURP_1511_3
{
public:
	/**
	 * @brief ITU-R P.1511-3, Annex 1, Section 1.1.
	 * 
	 * Topographic height of the surface of the Earth above mean sea level (m).
	 * 
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @return The topographic height of the surface of the Earth above mean sea level (m).
	 */
	static double TopographicHeight(double lat, double lon);

	/**
	 * @brief ITU-R P.1511-3, Annex 1, Section 1.1.
	 * 
	 * Geoid undulation (m), that is, the height difference between the WGS 84 geoid and the
	 * WGS 84 ellipsoid.
	 * 
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @return The Geoid undulation, h_EGM2008 (m), that is, the height difference between the
	 *         WGS 84 geoid and the WGS 84 ellipsoid.
	 */
	static double GeoidUndulation(double lat, double lon);

protected:
	static const DigitalMap s_TOPO_map;
	static const DigitalMap s_EGM2008_map;

private:
	// Prevent instantiation
	ITURP_1511_3() = delete;                                 // Delete default constructor
	ITURP_1511_3(const ITURP_1511_3&) = delete;              // Delete copy constructor
	ITURP_1511_3(ITURP_1511_3&&) = delete;                   // Delete move constructor
	ITURP_1511_3& operator=(const ITURP_1511_3&) = delete;   // Delete copy assignment
	ITURP_1511_3& operator=(ITURP_1511_3&&) = delete;        // Delete move assignment
};
