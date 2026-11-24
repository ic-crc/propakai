/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_676_13.h"
#include "ITURP_676_13.h"
#include "ITURP_835_6.h"


PROPAKAI_API double P676_13_GaseousAttenuation(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::GaseousAttenuation(f_GHz, p_hPa, T_K, rho_gm3);
	});
}

PROPAKAI_API double P676_13_DryAirGaseousAttenuation(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::DryAirGaseousAttenuation(f_GHz, p_hPa, T_K, rho_gm3);
	});
}

PROPAKAI_API double P676_13_WaterVapourGaseousAttenuation(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::WaterVapourGaseousAttenuation(f_GHz, p_hPa, T_K, rho_gm3);
	});
}

PROPAKAI_API double P676_13_SlantPathGaseousAttenuation(double f_GHz, double h1_km, double h2_km, double phi1_deg, int atm, double rho0_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathGaseousAttenuation(f_GHz, h1_km, h2_km, phi1_deg, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm), rho0_gm3);
	});
}

PROPAKAI_API double P676_13_SpaceBasedStationApparentElevAngle(double he_km, double hs_km, double phie_deg, int atm, double rho0_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SpaceBasedStationApparentElevAngle(he_km, hs_km, phie_deg, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm), rho0_gm3);
	});
}

PROPAKAI_API double P676_13_EarthBasedStationApparentElevAngle(double he_km, double hs_km, double phis_deg, int atm, double rho0_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::EarthBasedStationApparentElevAngle(he_km, hs_km, phis_deg, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm), rho0_gm3);
	});
}

PROPAKAI_API double P676_13_PhaseDispersion(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::PhaseDispersion(f_GHz, p_hPa, T_K, rho_gm3);
	});
}

PROPAKAI_API double P676_13_DownwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km, double hk_km, int atm, double rho0_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::DownwellingMicrowaveBrightnessTemperature(f_GHz, phi1_deg, h1_km, hk_km, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm), rho0_gm3);
	});
}

PROPAKAI_API double P676_13_UpwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km, double hk_km, int atm, double rho0_gm3, double emissivity, double TEarth_K)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::UpwellingMicrowaveBrightnessTemperature(f_GHz, phi1_deg, h1_km, hk_km, static_cast<ITURP_835_6::ReferenceAtmosphere>(atm), rho0_gm3, emissivity, TEarth_K);
	});
}

PROPAKAI_API double P676_13_SlantPathInstantOxygenGaseousAtt(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathInstantOxygenGaseousAtt(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3);
	});
}

PROPAKAI_API double P676_13_SlantPathStatisticalOxygenGaseousAtt(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathStatisticalOxygenGaseousAtt(f_GHz, theta_deg, p_percent, lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P676_13_SlantPathInstantWaterVapourGaseousAtt1(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathInstantWaterVapourGaseousAtt1(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3);
	});
}

PROPAKAI_API double P676_13_SlantPathInstantWaterVapourGaseousAtt2(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3, double Vs_kgm2)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathInstantWaterVapourGaseousAtt2(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3, Vs_kgm2);
	});
}

PROPAKAI_API double P676_13_SlantPathStatisticalWaterVapourGaseousAtt(double f_GHz, double theta_deg, double p_percent, double lat, double lon,  int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathStatisticalWaterVapourGaseousAtt(f_GHz, theta_deg, p_percent, lat, lon,  month, h_mamsl);
	});
}

PROPAKAI_API double P676_13_SlantPathInstantGaseousAttenuation(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3, double Vs_kgm2)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathInstantGaseousAttenuation(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3, Vs_kgm2);
	});
}

PROPAKAI_API double P676_13_SlantPathStatisticalGaseousAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::SlantPathStatisticalGaseousAttenuation(f_GHz, theta_deg, p_percent, lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P676_13_WeibullApproximation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_676_13::WeibullApproximation(f_GHz, theta_deg, p_percent, lat, lon, h_mamsl);
	});
}
