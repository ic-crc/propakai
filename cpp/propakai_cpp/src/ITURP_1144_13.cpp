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


// Bi-linear interpolation as documented in ITU-R P.1144-13, Annex 1, section 1b
double ITURP_1144_13::SquareGridBilinearInterpolation(const std::vector<double>& digitalMapVect, size_t numRows, size_t rowSize, double r, double c)
{
    if (numRows < 2 || rowSize < 2 || digitalMapVect.size() != (numRows*rowSize))
        return std::numeric_limits<double>::quiet_NaN();

    if (std::isnan(r) || std::isnan(c) || std::isinf(r) || std::isinf(c))
        return std::numeric_limits<double>::quiet_NaN();

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

bool ITURP_1144_13::InitDigitalMap(std::vector<double>& digitalMapVect, size_t expectedSize, const char* pathname)
{
    digitalMapVect.clear();
    constexpr size_t MAX_ALLOWED_SIZE = 50'000'000; // sanity limit
    if (!pathname || expectedSize == 0 || expectedSize > MAX_ALLOWED_SIZE)
        return false;

    try
	{
        digitalMapVect.resize(expectedSize);
    }
	catch (const std::exception&)
	{
		digitalMapVect.clear();
		return false;
	}

    if (!ReadDigitalMapFile_(digitalMapVect, pathname))
	{
        digitalMapVect.clear();
        return false;
    }

    return true;
}

bool ITURP_1144_13::ReadDigitalMapFile_(std::vector<double>& digitalMapVect, const char* pathname)
{
    std::ifstream txtFile(pathname);
    if (!txtFile.is_open())
        return false;

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
            return false; 
        digitalMapVect[arrayIndex++] = value;
    }

    // If the loop terminated before EOF, it means it hit corrupted/non-numeric data
    if (!txtFile.eof())
        return false; 

    // Destructor closes txtFile automatically

    return (arrayIndex == mapArraySize);
}
