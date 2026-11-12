/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once


class ITURP_1057_7
{
public:
	/**
	 * @brief Approximation for the inverse complementary cumulative distribution function, with
	 *        0 < p < 1.
	 *
	 * ITU-R P.1057-7, Annex 1, Section 3.
	 */
	static double Qinv(double p);

	/**
	 * @brief Approximation for the inverse cumulative distribution function, with 0 < p < 1.
	 *
	 * ITU-R P.1057-7, Annex 1, Section 3.
	 */
	static double Finv(double p);

private:
	// Prevent instantiation
	ITURP_1057_7() = delete;
	ITURP_1057_7(const ITURP_1057_7&) = delete;
	ITURP_1057_7(ITURP_1057_7&&) = delete;
	ITURP_1057_7& operator=(const ITURP_1057_7&) = delete;
	ITURP_1057_7& operator=(ITURP_1057_7&&) = delete;
};
