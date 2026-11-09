/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_1510_1.h"
#include <stdexcept>


#define MAKE_P1510_MAP(filename) \
    { filename, -90.0, +0.75, 241, -180.0, +0.75, 481, InterpolationType::Bilinear }

const DigitalMap ITURP_1510_1::s_TAnnual_map = MAKE_P1510_MAP("p1510_1/T_Annual.TXT");

const std::array<DigitalMap, 12> ITURP_1510_1::s_TMonth_maps = {{
	MAKE_P1510_MAP("p1510_1/T_Month01.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month02.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month03.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month04.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month05.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month06.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month07.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month08.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month09.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month10.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month11.TXT"),
	MAKE_P1510_MAP("p1510_1/T_Month12.TXT")
}};

#undef MAKE_P1510_MAP


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
