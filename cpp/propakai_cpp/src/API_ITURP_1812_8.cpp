/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_1812_8.h"
#include "ITURP_1812_8.h"


PROPAKAI_API bool P1812_8_Load_DN50_DigitalMap(const char* pathname)
{
	return ITURP_1812_8::Init_DN50(pathname);
}

PROPAKAI_API bool P1812_8_Load_N050_DigitalMap(const char* pathname)
{
	return ITURP_1812_8::Init_N050(pathname);
}

PROPAKAI_API double P1812_8_AUTO_CONSTANT()
{
	return ITURP_1812_8::AUTO;
}

PROPAKAI_API double P1812_8_BasicTransmissionloss(
	double f, double p, double pL, double latt, double lont, double latr, double lonr, 
	double htg, double hrg, bool vpol, unsigned int n, const double* d, const double* h,
	const int* cc, const double* rch, const double* sh, const int* rcz,
	double dct, double dcr, double deltaN, double N0, double wa)
{
	return ITURP_1812_8::BasicTransmissionloss(f, p, pL, latt, lont, latr, lonr, htg, hrg, vpol, n, d, h,
	                                           reinterpret_cast<const ITURP_1812_8::ClutterCategory*>(cc), rch, sh,
	                                           reinterpret_cast<const ITURP_1812_8::RadioClimaticZone*>(rcz), dct, dcr, deltaN, N0, wa);
}

PROPAKAI_API double P1812_8_FieldStrength(double f, double Lb)
{
	return ITURP_1812_8::FieldStrength(f, Lb);
}
