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
#include <filesystem>


class ITURP_1144_13
{
public:
	static void InitDigitalMap(std::vector<double>& digitalMapVect, size_t expectedSize, const std::filesystem::path& filePath);
	static double SquareGridBilinearInterpolation(const std::vector<double>& digitalMapVect, size_t numRows, size_t rowSize, double r, double c);

protected:
	static void ReadDigitalMapFile(std::vector<double>& digitalMapVect, const std::filesystem::path& filePath);

private:
	// Prevent instantiation
	ITURP_1144_13() = delete;
	ITURP_1144_13(const ITURP_1144_13&) = delete;
	ITURP_1144_13(ITURP_1144_13&&) = delete;
	ITURP_1144_13& operator=(const ITURP_1144_13&) = delete;
	ITURP_1144_13& operator=(ITURP_1144_13&&) = delete;
};