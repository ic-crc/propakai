/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once

#include <string>
#include <vector>
#include <mutex>
#include <cstddef>
#include "ITURP_1144_13.h"


enum class InterpolationType
{
	NearestNeighbor,
	Bilinear,
	Bicubic
};

class DigitalMap
{
public:
	// Static method to set the root directory for ALL DigitalMap instances.
	// Should be set once at startup.
	static void SetBaseDirectory(const std::string& directoryPath);

	// Constructor initializes all constant parameters
	DigitalMap(std::string filePath, // relative file path to the base directory
				double firstLat, double latSpacing, std::size_t numRows,
				double firstLon, double lonSpacing, std::size_t numCols,
				InterpolationType interpType);

	// Delete copy and move constructors/assignments because std::once_flag 
	// is neither copyable nor movable.
	DigitalMap(const DigitalMap&) = delete;
	DigitalMap& operator=(const DigitalMap&) = delete;
	DigitalMap(DigitalMap&&) = delete;
	DigitalMap& operator=(DigitalMap&&) = delete;

	// Thread-safe method to get the interpolated value at a given lat/lon.
	// Marked 'const' because logically it doesn't change the map's representation.
	double GetValue(double latitude, double longitude) const;

private:
	// Shared across all instances of DigitalMap
	static std::string s_baseDirectory;
	static std::mutex s_dirMutex; // Protects s_mainDirectory just in case

	const std::string m_relativeFilePath; // relative to s_mainDirectory
	const double m_firstLat;
	const double m_latSpacing;
	const std::size_t m_numRows;
	const double m_firstLon;
	const double m_lonSpacing;
	const std::size_t m_numCols;
	const InterpolationType m_interpType;

	// Lazy-loading state variables. 
	// 'mutable' allows them to be modified inside the const GetValue() function.
	mutable std::once_flag m_loadFlag;
	mutable std::vector<double> m_data;

	void LoadData() const;
};
