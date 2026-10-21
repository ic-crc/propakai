/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <cstddef>
#include <vector>


class ITURP_1144_13
{
public:
	static bool InitDigitalMap(std::vector<double>& digitalMapVect, int expectedSize, const char* pathname);
	static double SquareGridBilinearInterpolation(const double* mapArray, int numRows, int rowSize, double r, double c);

protected:
	static bool _ReadDigitalMapFile(double* mapArray, size_t mapArraySize, const char* pathname);

private:
	// Prevent instantiation
	ITURP_1144_13() = delete;                                  // Delete default constructor
	ITURP_1144_13(const ITURP_1144_13&) = delete;              // Delete copy constructor
	ITURP_1144_13(ITURP_1144_13&&) = delete;                   // Delete move constructor
	ITURP_1144_13& operator=(const ITURP_1144_13&) = delete;   // Delete copy assignment
	ITURP_1144_13& operator=(ITURP_1144_13&&) = delete;        // Delete move assignment
};