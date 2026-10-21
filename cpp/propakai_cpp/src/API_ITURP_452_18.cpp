/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_452_18.h"
#include "ITURP_452_18.h"


PROPAKAI_API bool P452_18_Load_DN50_DigitalMap(const char* pathname)
{
	return ITURP_452_18::Init_DN50(pathname);
}

PROPAKAI_API bool P452_18_Load_N050_DigitalMap(const char* pathname)
{
	return ITURP_452_18::Init_N050(pathname);
}

PROPAKAI_API double P452_18_AUTO_CONSTANT()
{
	return ITURP_452_18::AUTO;
}

PROPAKAI_API double P452_18_ClearAirBasicTransmissionLoss(
	double f, double p, bool worstMonth, double latt, double lont, double latr, double lonr,
	double htg, double hrg, double Gt, double Gr, bool vpol, unsigned int n, const double* d,
	const double* h, const int* cc, const double* rch, const int* rcz,
	double dct, double dcr, double P, double TC, double deltaN, double N0)
{
	return ITURP_452_18::ClearAirBasicTransmissionLoss(
		f, p, worstMonth, latt, lont, latr, lonr, htg, hrg, Gt, Gr, vpol, n, d, h,
		reinterpret_cast<const ITURP_452_18::ClutterCategory*>(cc), rch,
		reinterpret_cast<const ITURP_452_18::RadioClimaticZone*>(rcz), dct, dcr, P, TC, deltaN, N0);
}