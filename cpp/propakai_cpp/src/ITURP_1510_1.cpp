/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_1510_1.h"
#include <stdexcept>


DigitalMap make_p1510_1_map(const std::string& filename)
{
    return { filename, -90.0, +0.75, 241, -180.0, +0.75, 481, InterpolationType::Bilinear };
}

const DigitalMap ITURP_1510_1::s_TAnnual_map = make_p1510_1_map("p1510_1/T_Annual.TXT");

const std::vector<DigitalMap> ITURP_1510_1::s_TMonth_maps = []()
{
	std::vector<DigitalMap> maps;
	maps.reserve(12);

	for (int month = 1; month <= 12; ++month)
	{
		char filename[64];
		std::snprintf(filename, sizeof(filename), "p1510_1/T_Month%02d.TXT", month);
		maps.push_back(make_p1510_1_map(filename));
	}

	return maps;
}(); // () to execute the lambda immediately

double ITURP_1510_1::AnnualMeanSurfaceTemperature(double lat, double lon)
{
	return s_TAnnual_map.GetValue(lat, lon);
}

double ITURP_1510_1::MonthlyMeanSurfaceTemperature(double lat, double lon, int month)
{
	if (month < 1 || month > 12)
		throw std::invalid_argument("Month must be between 1 and 12.");

	std::size_t index = static_cast<std::size_t>(month-1);
	return s_TMonth_maps[index].GetValue(lat, lon);
}
