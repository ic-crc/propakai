/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once


class ITURP_2109_2
{
public:
	static double BuildingEntryLoss(double f_GHz, double probability_percent, double elevAngle_degrees, bool thermally_efficient);


private:
	// Prevent instantiation
	ITURP_2109_2() = delete;                                 // Delete default constructor
	ITURP_2109_2(const ITURP_2109_2&) = delete;              // Delete copy constructor
	ITURP_2109_2(ITURP_2109_2&&) = delete;                   // Delete move constructor
	ITURP_2109_2& operator=(const ITURP_2109_2&) = delete;   // Delete copy assignment
	ITURP_2109_2& operator=(ITURP_2109_2&&) = delete;        // Delete move assignment
};