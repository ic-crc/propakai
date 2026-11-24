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