/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_839_4.h"


const DigitalMap ITURP_839_4::s_h0_map("p839_4/h0.txt",
	+90.0, -1.5, 121, +0.0, +1.5, 241, InterpolationType::Bilinear);


double ITURP_839_4::MeanAnnual0CIsothermHeight(double lat, double lon)
{
	return s_h0_map.GetValue(lat, lon);
}

double ITURP_839_4::MeanAnnualRainHeight(double lat, double lon)
{
	return MeanAnnual0CIsothermHeight(lat, lon) + 0.36;
}
