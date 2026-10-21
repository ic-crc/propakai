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

PROPAKAI_API bool P1812_8_Load_DN50_DigitalMap(const char* pathname);

PROPAKAI_API bool P1812_8_Load_N050_DigitalMap(const char* pathname);

PROPAKAI_API double P1812_8_AUTO_CONSTANT();

PROPAKAI_API double P1812_8_BasicTransmissionloss(
	double f, double p, double pL, double latt, double lont, double latr, double lonr, 
	double htg, double hrg, bool vpol, unsigned int n, const double* d, const double* h,
	const int* cc, const double* rch, const double* sh, const int* rcz,
	double dct, double dcr, double deltaN, double N0, double wa);

PROPAKAI_API double P1812_8_FieldStrength(double f, double Lb);

#ifdef __cplusplus
}
#endif
