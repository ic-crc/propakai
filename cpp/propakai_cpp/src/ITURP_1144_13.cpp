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
#include <cmath>
#include <stdexcept>
#include <array>
#include <cstdlib> // std::strtod
#include <charconv>


// Bi-linear interpolation as documented in ITU-R P.1144-13, Annex 1, section 1b
double ITURP_1144_13::SquareGridBilinearInterpolation(const std::vector<double>& digitalMapVect, std::size_t numRows, std::size_t rowSize, double r, double c)
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

	std::size_t R = static_cast<std::size_t>(std::clamp(r, 0.0, maxR));
	std::size_t C = static_cast<std::size_t>(std::clamp(c, 0.0, maxC));

	double I00 = digitalMapVect[ R    * rowSize +  C   ];
	double I10 = digitalMapVect[(R+1) * rowSize +  C   ];
	double I01 = digitalMapVect[ R    * rowSize + (C+1)];
	double I11 = digitalMapVect[(R+1) * rowSize + (C+1)];
	double irc = I00*((R+1-r)*(C+1-c)) + I10*((r-R)*(C+1-c)) + I01*((R+1-r)*(c-C)) + I11*((r-R)*(c-C));

	return irc;
}

// Bi-cubic interpolation as documented in ITU-R P.1144-13, Annex 1, section 2
double ITURP_1144_13::SquareGridBicubicInterpolation(const std::vector<double>& digitalMapVect, std::size_t numRows, std::size_t rowSize, double r, double c)
{
    if (numRows < 4 || rowSize < 4)
		throw std::invalid_argument("Bicubic interpolation requires grid dimensions of at least 4x4.");

	if (digitalMapVect.size() != (numRows * rowSize))
		throw std::invalid_argument("Digital map vector size does not match the specified grid dimensions.");

	// std::isfinite returns false if the value is NaN or +/- Infinity
	if (!std::isfinite(r) || !std::isfinite(c))
		throw std::invalid_argument("Interpolation coordinates (r, c) must be finite numbers.");	

	double maxR = static_cast<double>(numRows-4);
	double maxC = static_cast<double>(rowSize-4);

    std::size_t R = static_cast<std::size_t>(std::clamp(std::trunc(r)-1.0, 0.0, maxR));
    std::size_t C = static_cast<std::size_t>(std::clamp(std::trunc(c)-1.0, 0.0, maxC));

	// original un-optimized code
	/*
	std::array<double, 4> RI = {0.0, 0.0, 0.0, 0.0};
	double I = 0.0;
    for (std::size_t ri_index = 0; ri_index < 4; ++ri_index)
	{
        std::size_t X = R + ri_index;
        for (std::size_t j = C; j < C + 4; ++j)
            RI[ri_index] += digitalMapVect[(X*rowSize)+j] * K(c-j);
    }
    for (std::size_t ri_index = 0; ri_index < 4; ++ri_index)
	{
        std::size_t i = R + ri_index;
        I += RI[ri_index] * K(r-i);
    }
	return I;
	*/

	// Optimized

	// Pre-calculate the column weights so we only call K() 4 times instead of 16
    const std::array<double, 4> col_weights = {K(c-(C+0)), K(c-(C+1)), K(c-(C+2)), K(c-(C+3))};
    double I = 0.0;
    for (std::size_t ri_index=0; ri_index<4; ++ri_index) // fused loop
	{
        std::size_t X = R + ri_index;
        std::size_t row_offset = X * rowSize;
        
        double ri_val = 0.0;
        for (std::size_t j_index=0; j_index<4; ++j_index)
            ri_val += digitalMapVect[row_offset+C+j_index] * col_weights[j_index];
        
        I += ri_val * K(r-X);
    }
    return I;
}

// bicubic interpolation kernel
double ITURP_1144_13::K(double d)
{
	constexpr double a = -0.5;
	double abs_d = std::abs(d);

	if (abs_d >= 2.0)
		return 0.0;
	else if (abs_d >= 1.0)
		return ((a*abs_d - 5.0*a)*abs_d + 8.0*a)*abs_d - 4.0*a;
	else
		return ((a + 2.0)*abs_d - (a + 3.0))*abs_d*abs_d + 1.0;
}

void ITURP_1144_13::InitDigitalMap(std::vector<double>& digitalMapVect, std::size_t expectedSize, const std::filesystem::path& filePath)
{
	digitalMapVect.clear();
	constexpr std::size_t MAX_ALLOWED_SIZE = 50'000'000; // sanity limit

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
#include <iostream>
void ITURP_1144_13::ReadDigitalMapFile(std::vector<double>& digitalMapVect, const std::filesystem::path& filePath)
{
    // Open in binary mode and jump to the end (ate) to get the exact file size
    std::ifstream txtFile(filePath, std::ios::binary | std::ios::ate);
    if (!txtFile.is_open())
        throw std::runtime_error("Failed to open digital map file: " + filePath.u8string());

    std::streamsize fileSize = txtFile.tellg();
    txtFile.seekg(0, std::ios::beg);

    // Read the entire file into memory in one single operation
    std::string buffer(static_cast<std::size_t>(fileSize), '\0');
    if (!txtFile.read(buffer.data(), fileSize))
        throw std::runtime_error("Failed to read digital map file: " + filePath.u8string());
    txtFile.close();

    // Parse doubles directly from the memory buffer
    const char* ptr = buffer.data();
    const char* endPtr = ptr + buffer.size();
    std::size_t arrayIndex = 0;
    std::size_t mapArraySize = digitalMapVect.size();
    while (ptr < endPtr)
	{
        // Skip whitespace (spaces, tabs, carriage returns, newlines)
        while (ptr < endPtr && (*ptr == ' ' || *ptr == '\n' || *ptr == '\r' || *ptr == '\t'))
            ++ptr;
        if (ptr >= endPtr)
            break; // Reached end of file cleanly
		// Skip a single optional leading '+' sign (since std::from_chars rejects leading '+')
		if (*ptr == '+')
			++ptr;

        // Parse the next double
        #if !defined(__cpp_lib_to_chars)
        char* nextPtr = nullptr;
        double value = std::strtod(ptr, &nextPtr); // from_chars may not be available on older linux, macOS
        if (ptr == nextPtr)
            throw std::runtime_error("Corrupted data in digital map file: " + filePath.u8string());
        #else
        double value = 0.0;
        std::from_chars_result res = std::from_chars(ptr, endPtr, value); // faster than strtod
		const char* nextPtr = res.ptr;
        if (res.ec != std::errc())
            throw std::runtime_error("Corrupted data in digital map file: " + filePath.u8string());
        #endif

        // If nextPtr didn't advance, we hit non-numeric/corrupted text
        if (ptr == nextPtr)
            throw std::runtime_error("Corrupted or non-numeric data encountered in digital map file: " + filePath.u8string());

        if (arrayIndex >= mapArraySize)
            throw std::runtime_error("Digital map file contains more data than expected: " + filePath.u8string());

        digitalMapVect[arrayIndex++] = value;
        ptr = nextPtr;
    }

    if (arrayIndex != mapArraySize)
        throw std::runtime_error("Digital map file contains less data than expected: " + filePath.u8string());
}
