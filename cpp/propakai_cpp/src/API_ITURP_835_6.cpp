/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_835_6.h"
#include "ITURP_835_6.h"


// Compile-time check
static_assert(static_cast<int>(P835_6_MEAN_ANNUAL_GLOBAL) == static_cast<int>(ITURP_835_6::ReferenceAtmosphere::MEAN_ANNUAL_GLOBAL));
static_assert(static_cast<int>(P835_6_LOW_LATITUDE) == static_cast<int>(ITURP_835_6::ReferenceAtmosphere::LOW_LATITUDE));
static_assert(static_cast<int>(P835_6_MID_LATITUDE_SUMMER) == static_cast<int>(ITURP_835_6::ReferenceAtmosphere::MID_LATITUDE_SUMMER));
static_assert(static_cast<int>(P835_6_MID_LATITUDE_WINTER) == static_cast<int>(ITURP_835_6::ReferenceAtmosphere::MID_LATITUDE_WINTER));
static_assert(static_cast<int>(P835_6_HIGH_LATITUDE_SUMMER) == static_cast<int>(ITURP_835_6::ReferenceAtmosphere::HIGH_LATITUDE_SUMMER));
static_assert(static_cast<int>(P835_6_HIGH_LATITUDE_WINTER) == static_cast<int>(ITURP_835_6::ReferenceAtmosphere::HIGH_LATITUDE_WINTER));


PROPAKAI_API double P835_6_Temperature(double h_km, int atm)
{
	return ExecuteSafely([&]() {
		return ITURP_835_6::Temperature(h_km, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm));
	});
}

PROPAKAI_API double P835_6_Pressure(double h_km, int atm)
{
	return ExecuteSafely([&]() {
		return ITURP_835_6::Pressure(h_km, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm));
	});
}

PROPAKAI_API double P835_6_WaterVapourDensity(double h_km, int atm, double rho0_gm3, double h0_km)
{
	return ExecuteSafely([&]() {
		return ITURP_835_6::WaterVapourDensity(h_km, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm), rho0_gm3, h0_km);
	});
}
