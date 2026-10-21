/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_2108_1.h"
#include "ITURP_2108_1.h"


PROPAKAI_API double P2108_1_HeightGainTerminalCorrection(double f_GHz, double h_m, int clut,
                                                                  double R_m/*=0.0*/, double ws_m/*=27.0*/)
{
	return ITURP_2108_1::HeightGainTerminalCorrection(f_GHz, h_m, static_cast<ITURP_2108_1::ClutterCategory>(clut), R_m, ws_m);
}

PROPAKAI_API double P2108_1_TerrestrialPathClutterLoss(double f_GHz, double distance_km, double location_percent)
{
	return ITURP_2108_1::TerrestrialPathClutterLoss(f_GHz, distance_km, location_percent);
}

PROPAKAI_API double P2108_1_EarthSpaceClutterLoss(double f_GHz, double theta_deg, double location_percent)
{
	return ITURP_2108_1::EarthSpaceClutterLoss(f_GHz, theta_deg, location_percent);
}
