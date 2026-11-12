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
	/**
	 * @brief Gets the building entry loss (dB).
	 *
	 * ITU-R P.2109-2, Annex 1, Section 3.
	 *
	 * @param f_GHz     Frequency (GHz), with 0.08 <= f_GHz <= 100.
	 * @param p_percent Probability that loss is not exceeded (%), with 1 <= p_percent <= 99.
	 * @param theta_deg Elevation angle of the path at the building façade (degrees above the
	 *                  horizontal), with -90 <= theta_deg <= 90.
	 * @param thermally_efficient Is building type thermally efficient or not (traditional).
	 *
	 * @return Building entry loss (dB).
	 */
	static double BuildingEntryLoss(double f_GHz, double p_percent, double theta_deg, bool thermally_efficient);


private:
	// Prevent instantiation
	ITURP_2109_2() = delete;
	ITURP_2109_2(const ITURP_2109_2&) = delete;
	ITURP_2109_2(ITURP_2109_2&&) = delete;
	ITURP_2109_2& operator=(const ITURP_2109_2&) = delete;
	ITURP_2109_2& operator=(ITURP_2109_2&&) = delete;
};