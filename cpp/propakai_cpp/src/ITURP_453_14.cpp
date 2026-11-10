/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_453_14.h"


const DigitalMap ITURP_453_14::s_NWET_Annual_50_map("p453_14/NWET_Annual_50.TXT",
	-90.0, +0.75, 241, -180.0, +0.75, 481, InterpolationType::Bilinear);


double ITURP_453_14::MedianAnnualNWet(double lat, double lon)
{
	return s_NWET_Annual_50_map.GetValue(lat, lon);
}
