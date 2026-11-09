/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "DigitalMap.h"

#include <filesystem>
#include <stdexcept>


// Initialize static members
std::string DigitalMap::s_baseDirectory = "";
std::mutex DigitalMap::s_dirMutex;


void DigitalMap::SetBaseDirectory(const std::string& directoryPath)
{
	std::lock_guard<std::mutex> lock(s_dirMutex);
	s_baseDirectory = directoryPath;
}

DigitalMap::DigitalMap(std::string relativeFilePath,
					   double firstLat, double latSpacing, std::size_t numRows,
					   double firstLon, double lonSpacing, std::size_t numCols,
					   InterpolationType interpType)
	: m_relativeFilePath(std::move(relativeFilePath)),
		m_firstLat(firstLat),
		m_latSpacing(latSpacing),
		m_numRows(numRows),
		m_firstLon(firstLon),
		m_lonSpacing(lonSpacing),
		m_numCols(numCols),
		m_interpType(interpType) 
{
}

double DigitalMap::GetValue(double latitude, double longitude) const
{
    if (!(std::abs(latitude) <= 90.0 && std::abs(longitude) <= 180.0))
        throw std::invalid_argument("Latitude must be in [-90, 90] and longitude in [-180, 180].");

    // Thread-safe Lazy Loading
    // std::call_once guarantees that LoadData() is executed only once.
    // If multiple threads hit this line at the same time, one will execute LoadData()
    // and the others will wait until it finishes before proceeding.
	// If LoadData() throws an exception, it will propagate up the chain.
	std::call_once(m_loadFlag, &DigitalMap::LoadData, this);

    // At this point, m_data is guaranteed to be populated and is only being read,
    // which is 100% thread-safe.

	if( longitude < 0 && m_firstLon >= 0 )
		longitude += 360;
	const double r = (latitude - m_firstLat) / m_latSpacing;
	const double c = (longitude - m_firstLon) / m_lonSpacing;

	switch (m_interpType)
	{
		case InterpolationType::NearestNeighbor:
			throw std::logic_error("Nearest Neighbor interpolation is not implemented yet.");
		case InterpolationType::Bilinear:
			return ITURP_1144_13::SquareGridBilinearInterpolation(m_data, m_numRows, m_numCols, r, c);
		case InterpolationType::Bicubic:
			return ITURP_1144_13::SquareGridBicubicInterpolation(m_data, m_numRows, m_numCols, r, c);
		default:
			throw std::logic_error("Unexpected InterpolationType encountered in DigitalMap::GetValue.");
	}
}

void DigitalMap::LoadData() const
{
	// Safely read the base directory
	std::string baseDir;
	{
		std::lock_guard<std::mutex> lock(s_dirMutex);
		baseDir = s_baseDirectory;
	}

    // Use u8path() to safely convert UTF-8 strings (e.g., "C:/Users/René") 
    // into Windows native wide-characters under the hood.
    std::filesystem::path fullPath = std::filesystem::u8path(baseDir) / m_relativeFilePath;

	ITURP_1144_13::InitDigitalMap(m_data, m_numRows*m_numCols, fullPath);
}
