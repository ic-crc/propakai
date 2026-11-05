/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_1144_13.h"
#include <algorithm>
#include <fstream>
#include <string>
#include <limits>
#include <cmath>
#include <locale>
#include <stdexcept>


// Bi-linear interpolation as documented in ITU-R P.1144-13, Annex 1, section 1b
double ITURP_1144_13::SquareGridBilinearInterpolation(const std::vector<double>& digitalMapVect, size_t numRows, size_t rowSize, double r, double c)
{
	if (numRows < 2 || rowSize < 2)
		throw std::invalid_argument("Bilinear interpolation requires grid dimensions of at least 2x2.");

	if (digitalMapVect.size() != (numRows * rowSize))
		throw std::invalid_argument("Digital map vector size does not match the specified grid dimensions.");

	// std::isfinite returns false if the value is NaN or +/- Infinity
	if (!std::isfinite(r) || !std::isfinite(c))
		throw std::invalid_argument("Interpolation coordinates (r, c) must be finite numbers.");

	double maxR = static_cast<double>(numRows-2);
	double maxC = static_cast<double>(rowSize-2);

	size_t R = static_cast<size_t>(std::clamp(r, 0.0, maxR));
	size_t C = static_cast<size_t>(std::clamp(c, 0.0, maxC));

	double I00 = digitalMapVect[ R    * rowSize +  C   ];
	double I10 = digitalMapVect[(R+1) * rowSize +  C   ];
	double I01 = digitalMapVect[ R    * rowSize + (C+1)];
	double I11 = digitalMapVect[(R+1) * rowSize + (C+1)];
	double irc = I00*((R+1-r)*(C+1-c)) + I10*((r-R)*(C+1-c)) + I01*((R+1-r)*(c-C)) + I11*((r-R)*(c-C));

	return irc;
}

void ITURP_1144_13::InitDigitalMap(std::vector<double>& digitalMapVect, size_t expectedSize, const std::filesystem::path& filePath)
{
	digitalMapVect.clear();
	constexpr size_t MAX_ALLOWED_SIZE = 50'000'000; // sanity limit

	if (filePath.empty())
		throw std::invalid_argument("Digital map file path cannot be empty.");

	if (expectedSize == 0 || expectedSize > MAX_ALLOWED_SIZE)
		throw std::invalid_argument("Invalid expected size for digital map: " + std::to_string(expectedSize));

	try 
	{
		digitalMapVect.resize(expectedSize); // may throw std::bad_alloc   
		ReadDigitalMapFile(digitalMapVect, filePath);
	}
	catch (...) 
	{
		// Guarantee that the vector is left empty if ANYTHING goes wrong 
		digitalMapVect.clear();
		throw; 
	}
}

void ITURP_1144_13::ReadDigitalMapFile(std::vector<double>& digitalMapVect, const std::filesystem::path& filePath)
{
	std::ifstream txtFile(filePath);
	if (!txtFile.is_open())
		throw std::runtime_error("Failed to open digital map file: " + filePath.u8string());

	// Ensure '.' is always the decimal separator
	txtFile.imbue(std::locale::classic());

	size_t arrayIndex = 0;
	size_t mapArraySize = digitalMapVect.size();
	double value = 0.0;

	// The >> operator automatically skips all whitespace (spaces, tabs, newlines)
	// and safely parses the double, setting failbit if invalid characters are found.
	while (txtFile >> value) 
	{
		if (arrayIndex >= mapArraySize)
			throw std::runtime_error("Digital map file contains more data than expected: " + filePath.u8string());
		digitalMapVect[arrayIndex++] = value;
	}

	// If the loop terminated before EOF, it means it hit corrupted/non-numeric data
	if (!txtFile.eof())
		throw std::runtime_error("Corrupted or non-numeric data encountered in digital map file: " + filePath.u8string());

    if (arrayIndex != mapArraySize)
        throw std::runtime_error("Digital map file contains less data than expected: " + filePath.u8string());

	// Destructor closes txtFile automatically
}
