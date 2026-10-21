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
	static double Qinv(double p);
	static double Finv(double p);

private:
	// Prevent instantiation
	ITURP_1057_7() = delete;                                 // Delete default constructor
	ITURP_1057_7(const ITURP_1057_7&) = delete;              // Delete copy constructor
	ITURP_1057_7(ITURP_1057_7&&) = delete;                   // Delete move constructor
	ITURP_1057_7& operator=(const ITURP_1057_7&) = delete;   // Delete copy assignment
	ITURP_1057_7& operator=(ITURP_1057_7&&) = delete;        // Delete move assignment
};
