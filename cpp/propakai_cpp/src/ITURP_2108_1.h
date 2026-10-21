/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once


class ITURP_2108_1
{
public:
	enum ClutterCategory : int
	{
		WATER_SEA           = 1,
		OPEN_RURAL          = 2,
		SUBURBAN            = 3,
		URBAN_TREES_FOREST  = 4,
		DENSE_URBAN         = 5
	};

	static double HeightGainTerminalCorrection(double f_GHz, double h_m, ITURP_2108_1::ClutterCategory clut, double R_m=0.0, double ws_m=27.0);
	static double TerrestrialPathClutterLoss(double f_GHz, double distance_km, double location_percent);
	static double EarthSpaceClutterLoss(double f_GHz, double theta_deg, double location_percent);

private:
	// Prevent instantiation
	ITURP_2108_1() = delete;                                 // Delete default constructor
	ITURP_2108_1(const ITURP_2108_1&) = delete;              // Delete copy constructor
	ITURP_2108_1(ITURP_2108_1&&) = delete;                   // Delete move constructor
	ITURP_2108_1& operator=(const ITURP_2108_1&) = delete;   // Delete copy assignment
	ITURP_2108_1& operator=(ITURP_2108_1&&) = delete;        // Delete move assignment
};
