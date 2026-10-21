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


// Bi-linear interpolation as documented in ITU-R P.1144-13, Annex 1, section 1b
double ITURP_1144_13::SquareGridBilinearInterpolation(const double* mapArray, int numRows, int rowSize, double r, double c)
{
int R, C;
double irc, I00, I01, I10, I11;

	R = static_cast<int>(r);
	R = std::max(R, 0);
	R = std::min(R, numRows-2);
	C = static_cast<int>(c);
	C = std::max(C, 0);
	C = std::min(C, rowSize-2);
	I00 = mapArray[ R    * rowSize +  C   ];
	I10 = mapArray[(R+1) * rowSize +  C   ];
	I01 = mapArray[ R    * rowSize + (C+1)];
	I11 = mapArray[(R+1) * rowSize + (C+1)];
	irc = I00*((R+1-r)*(C+1-c)) + I10*((r-R)*(C+1-c)) + I01*((R+1-r)*(c-C)) + I11*((r-R)*(c-C));

	return irc;
}

bool ITURP_1144_13::InitDigitalMap(std::vector<double>& digitalMapVect, int expectedSize, const char* pathname)
{
	digitalMapVect.resize(static_cast<size_t>(expectedSize));
	if( _ReadDigitalMapFile(digitalMapVect.data(), digitalMapVect.size(), pathname) == false )
	{
		digitalMapVect.resize(0);
		return false;
	}
	return true;
}

bool ITURP_1144_13::_ReadDigitalMapFile(double* mapArray, size_t mapArraySize, const char* pathname)
{
std::ifstream txtFile(pathname);
std::string line;
size_t arrayIndex = 0;
const std::string delims = " \t";

	while (std::getline(txtFile, line))
	{
		size_t start = line.find_first_not_of(delims);
		while (start != std::string::npos)
		{
			size_t end = line.find_first_of(delims, start);
			std::string token = line.substr(start, end - start);
			if (!token.empty())
			{
				if( arrayIndex < mapArraySize )
					mapArray[arrayIndex] = atof(token.c_str());
				arrayIndex++;
			}
			start = line.find_first_not_of(delims, end);
		}
	}
	txtFile.close();

	return (arrayIndex == mapArraySize);
}