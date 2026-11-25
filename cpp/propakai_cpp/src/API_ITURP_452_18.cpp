/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_452_18.h"
#include "ITURP_452_18.h"


static_assert(static_cast<int>(P452_18_COASTAL_LAND) == static_cast<int>(ITURP_452_18::RadioClimaticZone::COASTAL_LAND));
static_assert(static_cast<int>(P452_18_INLAND) == static_cast<int>(ITURP_452_18::RadioClimaticZone::INLAND));
static_assert(static_cast<int>(P452_18_SEA) == static_cast<int>(ITURP_452_18::RadioClimaticZone::SEA));

static_assert(static_cast<int>(P452_18_WATER_SEA) == static_cast<int>(ITURP_452_18::ClutterCategory::WATER_SEA));
static_assert(static_cast<int>(P452_18_OPEN_RURAL) == static_cast<int>(ITURP_452_18::ClutterCategory::OPEN_RURAL));
static_assert(static_cast<int>(P452_18_SUBURBAN) == static_cast<int>(ITURP_452_18::ClutterCategory::SUBURBAN));
static_assert(static_cast<int>(P452_18_URBAN_TREES_FOREST) == static_cast<int>(ITURP_452_18::ClutterCategory::URBAN_TREES_FOREST));
static_assert(static_cast<int>(P452_18_DENSE_URBAN) == static_cast<int>(ITURP_452_18::ClutterCategory::DENSE_URBAN));

// Can't use std::isnan() within static_assert() in C++ 17 since std::isnan() is not constexpr.
// The following trick works instead since NaN is the only value that does not equal itself.
static_assert(PROPAKAI_AUTO != PROPAKAI_AUTO && ITURP_452_18::AUTO != ITURP_452_18::AUTO, "AUTO must be NaN");
//static_assert(std::isnan(PROPAKAI_AUTO) && std::isnan(ITURP_1812_8::AUTO)); // does not compile on CLang


PROPAKAI_API double P452_18_ClearAirBasicTransmissionLoss(
	double f_GHz, double p_percent, bool worstMonth, double latt, double lont, double latr, double lonr,
	double htg_m, double hrg_m, double Gt_dBi, double Gr_dBi, bool vpol, unsigned int n, const double* d_km,
	const double* h_mamsl, const int* cc, const double* rch_m, const int* rcz, double dct_km, double dcr_km,
	double P_hPa, double T_C, double deltaN, double N0)
{
	return ExecuteSafely([&]() {
		return ITURP_452_18::ClearAirBasicTransmissionLoss(
			f_GHz, p_percent, worstMonth, latt, lont, latr, lonr,
			htg_m, hrg_m, Gt_dBi, Gr_dBi, vpol, n, d_km, h_mamsl,
			reinterpret_cast<const ITURP_452_18::ClutterCategory*>(cc),
			rch_m,
			reinterpret_cast<const ITURP_452_18::RadioClimaticZone*>(rcz),
			dct_km, dcr_km, P_hPa, T_C, deltaN, N0);
	});
}
