/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once

#include "API_PropaKai.h"
#include "API_ITURP_835_6.h"

#ifdef __cplusplus
	#define DEFARG(val) = val
#else
	// For C-compatibilty (does not support default arguments)
	#define DEFARG(val)
#endif

#ifdef __cplusplus
extern "C" {
#endif

PROPAKAI_API double P676_13_GaseousAttenuation(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_DryAirGaseousAttenuation(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_WaterVapourGaseousAttenuation(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_SlantPathGaseousAttenuation(double f_GHz, double h1_km, double h2_km, double phi1_deg, int atm DEFARG(P835_6_MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_SpaceBasedStationApparentElevAngle(double he_km, double hs_km, double phie_deg, int atm DEFARG(P835_6_MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_EarthBasedStationApparentElevAngle(double he_km, double hs_km, double phis_deg, int atm DEFARG(P835_6_MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_PhaseDispersion(double f_GHz, double p_hPa DEFARG(1013.25), double T_K DEFARG(288.15), double rho_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_DownwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km DEFARG(0.0), double hk_km DEFARG(100.1), int atm DEFARG(P835_6_MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5));
PROPAKAI_API double P676_13_UpwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km DEFARG(0.0), double hk_km DEFARG(100.1), int atm DEFARG(P835_6_MEAN_ANNUAL_GLOBAL), double rho0_gm3 DEFARG(7.5), double emissivity DEFARG(0.95), double TEarth_K DEFARG(290.0));
PROPAKAI_API double P676_13_SlantPathInstantOxygenGaseousAtt(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3);
PROPAKAI_API double P676_13_SlantPathStatisticalOxygenGaseousAtt(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month DEFARG(-1), double h_mamsl DEFARG(PROPAKAI_AUTO));
PROPAKAI_API double P676_13_SlantPathInstantWaterVapourGaseousAtt1(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3);
PROPAKAI_API double P676_13_SlantPathInstantWaterVapourGaseousAtt2(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3, double Vs_kgm2);
PROPAKAI_API double P676_13_SlantPathStatisticalWaterVapourGaseousAtt(double f_GHz, double theta_deg, double p_percent, double lat, double lon,  int month DEFARG(-1), double h_mamsl DEFARG(PROPAKAI_AUTO));
PROPAKAI_API double P676_13_SlantPathInstantGaseousAttenuation(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3, double Vs_kgm2 DEFARG(PROPAKAI_NONE));
PROPAKAI_API double P676_13_SlantPathStatisticalGaseousAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month DEFARG(-1), double h_mamsl DEFARG(PROPAKAI_AUTO));
PROPAKAI_API double P676_13_WeibullApproximation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, double h_mamsl DEFARG(PROPAKAI_AUTO));

#ifdef __cplusplus
}
#endif

#undef DEFARG
