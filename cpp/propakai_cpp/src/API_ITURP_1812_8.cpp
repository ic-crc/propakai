/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_1812_8.h"
#include "ITURP_1812_8.h"


static_assert(static_cast<int>(P1812_8_COASTAL_LAND) == static_cast<int>(ITURP_1812_8::RadioClimaticZone::COASTAL_LAND));
static_assert(static_cast<int>(P1812_8_INLAND) == static_cast<int>(ITURP_1812_8::RadioClimaticZone::INLAND));
static_assert(static_cast<int>(P1812_8_SEA) == static_cast<int>(ITURP_1812_8::RadioClimaticZone::SEA));

static_assert(static_cast<int>(P1812_8_WATER_SEA) == static_cast<int>(ITURP_1812_8::ClutterCategory::WATER_SEA));
static_assert(static_cast<int>(P1812_8_OPEN_RURAL) == static_cast<int>(ITURP_1812_8::ClutterCategory::OPEN_RURAL));
static_assert(static_cast<int>(P1812_8_SUBURBAN) == static_cast<int>(ITURP_1812_8::ClutterCategory::SUBURBAN));
static_assert(static_cast<int>(P1812_8_URBAN_TREES_FOREST) == static_cast<int>(ITURP_1812_8::ClutterCategory::URBAN_TREES_FOREST));
static_assert(static_cast<int>(P1812_8_DENSE_URBAN) == static_cast<int>(ITURP_1812_8::ClutterCategory::DENSE_URBAN));

// Can't use std::isnan() within static_assert() in C++ 17 since std::isnan() is not constexpr.
// The following trick works instead since NaN is the only value that does not equal itself.
static_assert(PROPAKAI_AUTO != PROPAKAI_AUTO && ITURP_1812_8::AUTO != ITURP_1812_8::AUTO, "AUTO must be NaN");
//static_assert(std::isnan(PROPAKAI_AUTO) && std::isnan(ITURP_1812_8::AUTO)); // does not compile on CLang


PROPAKAI_API double P1812_8_BasicTransmissionloss(
	double f_GHz, double p_percent, double pL_percent, double latt, double lont, double latr, double lonr,
	double htg_m, double hrg_m, bool vpol, unsigned int n, const double* d_km, const double* h_mamsl,
	const int* cc, const double* rch_m, const double* sh_mamsl,
	const int* rcz, double dct_km, double dcr_km,
	double deltaN, double N0, double wa_m)
{
	return ExecuteSafely([&]() {
		return ITURP_1812_8::BasicTransmissionloss(f_GHz, p_percent, pL_percent, latt, lont, latr, lonr,
												   htg_m, hrg_m, vpol, n, d_km, h_mamsl,
												   reinterpret_cast<const ITURP_1812_8::ClutterCategory*>(cc),
												   rch_m, sh_mamsl,
												   reinterpret_cast<const ITURP_1812_8::RadioClimaticZone*>(rcz),
												   dct_km, dcr_km, deltaN, N0, wa_m);
	});
}

PROPAKAI_API double P1812_8_FieldStrength(double f_GHz, double Lb_dB)
{
	return ExecuteSafely([&]() {
		return ITURP_1812_8::FieldStrength(f_GHz, Lb_dB);
	});
}
