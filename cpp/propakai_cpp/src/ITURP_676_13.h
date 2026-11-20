/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <utility> // for std::pair
#include "ITURP_835_6.h"


class ITURP_676_13
{
public:
	using Atm = ITURP_835_6::ReferenceAtmosphere;

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 1.
	 * 
	 * Gaseous attenuation attributable to dry air and water vapour (dB/km).
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 1000.
	 * @param p_hPa (Optional) Atmospheric pressure (hPa). Defaults to 1013.25.
	 * @param T_K (Optional) Temperature (K). Defaults to 288.15.
	 * @param rho_gm3 (Optional) Water vapour density (g/m3). Defaults to 7.5.
	 * @return Gaseous attenuation attributable to dry air and water vapour, gamma (dB/km).
	 */
	static double GaseousAttenuation(double f_GHz, double p_hPa=1013.25, double T_K=288.15, double rho_gm3=7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 1.
	 * 
	 * Specific gaseous attenuation attributable to dry air (dB/km).
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 1000.
	 * @param p_hPa (Optional) Atmospheric pressure (hPa). Defaults to 1013.25.
	 * @param T_K (Optional) Temperature (K). Defaults to 288.15.
	 * @param rho_gm3 (Optional) Water vapour density (g/m3). Defaults to 7.5.
	 * @return Specific gaseous attenuation attributable to dry air (oxygen, pressure-induced
	 *         nitrogen and non-resonant Debye attenuation), gamma_o, in dB/km.
	 */
	static double DryAirGaseousAttenuation(double f_GHz, double p_hPa=1013.25, double T_K=288.15, double rho_gm3=7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 1.
	 * 
	 * Specific gaseous attenuation attributable to water vapour (dB/km).
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 1000.
	 * @param p_hPa (Optional) Atmospheric pressure (hPa). Defaults to 1013.25.
	 * @param T_K (Optional) Temperature (K). Defaults to 288.15.
	 * @param rho_gm3 (Optional) Water vapour density (g/m3). Defaults to 7.5.
	 * @return Specific gaseous attenuation attributable to water vapour, gamma_w (dB/km).
	 */
	static double WaterVapourGaseousAttenuation(double f_GHz, double p_hPa=1013.25, double T_K=288.15, double rho_gm3=7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 2.2.
	 * 
	 * Calculates the Earth-space slant path gaseous attenuation for an ascending path between a
	 * location on or near the surface of the Earth and a location above the surface of the Earth or
	 * in space.
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 1000.
	 * @param h1_km Height of the first station (km), with 0 <= h1_km < h2_km.
	 * @param h2_km Height of the second station (km), with 0 <= h1_km < h2_km.
	 * @param phi1_deg The local apparent elevation angle at height h1_km (degrees).
	 *                 0 deg=horizon, +90 deg=zenith, -90 deg=nadir.
	 * @param atm (Optional) A reference atmosphere from ITU-R P.835-6.
	 *            Default value is MEAN_ANNUAL_GLOBAL.
	 * @param rho0_gm3 (Optional) Ground-level water vapour density (g/m3). Only applies when atm
	 *                 is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
	 * @return The slant path gaseous attenuation, Agas (dB).
	 */
	static double SlantPathGaseousAttenuation(double f_GHz, double h1_km, double h2_km, double phi1_deg, Atm atm = Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3 = 7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 2.2.3.
	 * 
	 * Calculates the apparent elevation angle at the space-based station based on the apparent
	 * elevation angle at the Earth-based station.
	 * 
	 * "The gaseous attenuation for a space-Earth path, where the apparent elevation angle at the space
	 * station is [phis_deg], is identical to the gaseous attenuation for the reciprocal Earth-space
	 * path, where the apparent elevation angle at the earth station is [phie_deg]".
	 * 
	 * @param he_km Height of the Earth-based station (km).
	 * @param hs_km Height of the space-based station (km).
	 * @param phie_deg Apparent elevation angle at the Earth-based station (degrees).
	 *                 0 deg=horizon, +90 deg=zenith, -90 deg=nadir.
	 * @param atm (Optional) A reference atmosphere from ITU-R P.835-6.
	 *            Default value is MEAN_ANNUAL_GLOBAL.
	 * @param rho0_gm3 (Optional) Ground-level water vapour density (g/m3). Only applies when atm
	 *                 is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
	 * @return Apparent elevation angle at the space-based station, phis_deg (degrees).
	 */
	static double SpaceBasedStationApparentElevAngle(double he_km, double hs_km, double phie_deg, Atm atm = Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3 = 7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 2.2.3.
	 * 
	 * Calculates the apparent elevation angle at the Earth-based station based on the apparent
	 * elevation angle at the space-based station.
	 * 
	 * "The gaseous attenuation for a space-Earth path, where the apparent elevation angle at the space
	 * station is [phis_deg], is identical to the gaseous attenuation for the reciprocal Earth-space
	 * path, where the apparent elevation angle at the earth station is [phie_deg]".
	 * 
	 * @param he_km Height of the Earth-based station (km).
	 * @param hs_km Height of the space-based station (km).
	 * @param phis_deg Apparent elevation angle at the space-based station (degrees).
	 *                 0 deg=horizon, +90 deg=zenith, -90 deg=nadir.
	 * @param atm (Optional) A reference atmosphere from ITU-R P.835-6.
	 *            Default value is MEAN_ANNUAL_GLOBAL.
	 * @param rho0_gm3 (Optional) Ground-level water vapour density (g/m3). Only applies when atm
	 *                 is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
	 * @return Reciprocal apparent elevation angle at the Earth-based station, phie_deg (degrees).
	 */
	static double EarthBasedStationApparentElevAngle(double he_km, double hs_km, double phis_deg, Atm atm = Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3 = 7.5);

protected:
	static double NppOxygen(double f_GHz, double p_hPa, double T_K, double rho_gm3);
	static double NppWaterVapour(double f_GHz, double p_hPa, double T_K, double rho_gm3);
	static double RefractiveIndex(double h_km, Atm atm=Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3=7.5);
	static std::pair<int, int> LayerIndices(double h_lower, double h_upper);
	static double LayerThickness(int i, int i_lower, int i_upper, double h_lower, double h_upper);
	static double LayerBottomHeight(int i, int i_lower, int i_upper, double h_lower, double h_upper);
	static double NonNegElevAnglSlantPathGaseousAtt(double f_GHz, double h1_km, double h2_km, double phi1_deg, Atm atm, double rho0_gm3);
	static double NegElevAnglSlantPathGaseousAtt(double f_GHz, double h1_km, double h2_km, double phi1_deg, Atm atm, double rho0_gm3);

	static const double s_TABLE_1[44][7];
	static const double s_TABLE_2[35][7];

private:
	// Prevent instantiation
	ITURP_676_13() = delete;
	ITURP_676_13(const ITURP_676_13&) = delete;
	ITURP_676_13(ITURP_676_13&&) = delete;
	ITURP_676_13& operator=(const ITURP_676_13&) = delete;
	ITURP_676_13& operator=(ITURP_676_13&&) = delete;
};