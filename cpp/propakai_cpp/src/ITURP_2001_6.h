/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <vector>
	

class ITURP_2001_6
{
public:
	static void GreatCircleIntermediatePoint(double lat0, double lon0, double lat1, double lon1, double distKm, double& intermLat, double& intermLon);
	static double Wavelength(double f_GHz);

	// Rec. ITU-R P.2001-6, Section 2.3 of Annex
	static constexpr double Re = 6371.0; // Average Earth radius (km)
	static constexpr double c = 2.998E8; // Speed of propagation (m/s)

private:
	// Prevent instantiation
	ITURP_2001_6() = delete;                                 // Delete default constructor
	ITURP_2001_6(const ITURP_2001_6&) = delete;              // Delete copy constructor
	ITURP_2001_6(ITURP_2001_6&&) = delete;                   // Delete move constructor
	ITURP_2001_6& operator=(const ITURP_2001_6&) = delete;   // Delete copy assignment
	ITURP_2001_6& operator=(ITURP_2001_6&&) = delete;        // Delete move assignment
};