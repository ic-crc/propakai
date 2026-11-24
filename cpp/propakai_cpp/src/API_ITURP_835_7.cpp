/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_835_7.h"
#include "ITURP_835_7.h"


// Compile-time check
static_assert(static_cast<int>(P835_7_ITU_R) == static_cast<int>(ITURP_835_7::ReferenceAtmosphere::ITU_R));
static_assert(static_cast<int>(P835_7_SEASONAL_SUMMER) == static_cast<int>(ITURP_835_7::ReferenceAtmosphere::SEASONAL_SUMMER));
static_assert(static_cast<int>(P835_7_SEASONAL_WINTER) == static_cast<int>(ITURP_835_7::ReferenceAtmosphere::SEASONAL_WINTER));


PROPAKAI_API double P835_7_Temperature(double z_km, int atm, double lat)
{
	return ExecuteSafely([&]() {
		return ITURP_835_7::Temperature(z_km, static_cast<ITURP_835_7::ReferenceAtmosphere>(atm), lat);
	});
}

PROPAKAI_API double P835_7_Pressure(double z_km, int atm, double lat)
{
	return ExecuteSafely([&]() {
		return ITURP_835_7::Pressure(z_km, static_cast<ITURP_835_7::ReferenceAtmosphere>(atm), lat);
	});
}

PROPAKAI_API double P835_7_WaterVapourDensity(double z_km, int atm, double lat)
{
	return ExecuteSafely([&]() {
		return ITURP_835_7::WaterVapourDensity(z_km, static_cast<ITURP_835_7::ReferenceAtmosphere>(atm), lat);
	});
}
