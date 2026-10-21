/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once

#include "API_PropaKai.h"

#ifdef __cplusplus
extern "C" {
#endif

PROPAKAI_API bool P452_18_Load_DN50_DigitalMap(const char* pathname);

PROPAKAI_API bool P452_18_Load_N050_DigitalMap(const char* pathname);

PROPAKAI_API double P452_18_AUTO_CONSTANT();

PROPAKAI_API double P452_18_ClearAirBasicTransmissionLoss(
	double f, double p, bool worstMonth, double latt, double lont, double latr, double lonr,
	double htg, double hrg, double Gt, double Gr, bool vpol, unsigned int n, const double* d,
	const double* h, const int* cc, const double* rch, const int* rcz,
	double dct, double dcr, double P, double TC, double deltaN, double N0);

#ifdef __cplusplus
}
#endif
