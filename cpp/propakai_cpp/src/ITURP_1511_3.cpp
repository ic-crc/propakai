/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_1511_3.h"


const DigitalMap ITURP_1511_3::s_TOPO_map("p1511_3/TOPO.dat",
	+90.125, -(1.0/12.0), 2164, -180.125, +(1.0/12.0), 4324, InterpolationType::Bicubic);

const DigitalMap ITURP_1511_3::s_EGM2008_map("p1511_3/EGM2008.txt",
	+90+(2.0/12.0), -(1.0/12.0), 2165, -180-(2.0/12.0), +1.0/12.0, 4325, InterpolationType::Bicubic);


double ITURP_1511_3::TopographicHeight(double lat, double lon)
{
	return s_TOPO_map.GetValue(lat, lon);
}


double ITURP_1511_3::GeoidUndulation(double lat, double lon)
{
	return s_EGM2008_map.GetValue(lat, lon);
}
