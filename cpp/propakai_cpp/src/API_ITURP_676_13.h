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
	#define DEFARG(val) = val
	extern "C" {
#else
	// For C-compatibilty (does not support default arguments)
	#define DEFARG(val)
#endif

typedef enum {
	MEAN_ANNUAL_GLOBAL   = 1,
	LOW_LATITUDE         = 2,
	MID_LATITUDE_SUMMER  = 3,
	MID_LATITUDE_WINTER  = 4,
	HIGH_LATITUDE_SUMMER = 5,
	HIGH_LATITUDE_WINTER = 6,
} ReferenceAtmosphere;

PROPAKAI_API double P676_13_GaseousAttenuation(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_DryAirGaseousAttenuation(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_WaterVapourGaseousAttenuation(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_SlantPathGaseousAttenuation(double f_GHz, double h1_km, double h2_km, double phi1_deg, int atm DEFARG(MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_SpaceBasedStationApparentElevAngle(double he_km, double hs_km, double phie_deg, int atm DEFARG(MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_EarthBasedStationApparentElevAngle(double he_km, double hs_km, double phis_deg, int atm DEFARG(MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_PhaseDispersion(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_DownwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km DEFARG(0.0), double hk_km DEFARG(100.1), int atm DEFARG(MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_UpwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km DEFARG(0.0), double hk_km DEFARG(100.1), int atm DEFARG(MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5), double emissivity DEFARG(0.95), double TEarth_K DEFARG(290.0));
PROPAKAI_API double P676_13_SlantPathInstantOxygenGaseousAtt(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3);

#ifdef __cplusplus
	}
#endif
