/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <utility> // for std::pair
#include <tuple>
#include "ITURP_835_6.h"
#include "DigitalMap.h"


class ITURP_676_13
{
public:
	using ReferenceAtmosphere = ITURP_835_6::ReferenceAtmosphere;
	using Atm = ITURP_835_6::ReferenceAtmosphere;

	static constexpr double AUTO = std::numeric_limits<double>::quiet_NaN();
	static constexpr double NONE = std::numeric_limits<double>::quiet_NaN();

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

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 3.
	 * 
	 * Calculates the gaseous phase dispersion (deg/km).
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 1000.
	 * @param p_hPa (Optional) Atmospheric pressure (hPa). Defaults to 1013.25.
	 * @param T_K (Optional) Temperature (K). Defaults to 288.15.
	 * @param rho_gm3 (Optional) Water vapour density (g/m3). Defaults to 7.5.
	 * @return The gaseous phase dispersion, phi (deg/km).
	 */
	static double PhaseDispersion(double f_GHz, double p_hPa = 1013.25, double T_K = 288.15, double rho_gm3 = 7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 4.1.
	 * 
	 * The downwelling atmospheric microwave brightness temperature (K).
	 * 
	 * @param f_GHz Frequency in GHz, with 1 <= f_GHz <= 1000.
	 * @param phi1_deg The local apparent elevation angle at height h1_km (degrees), 
	 *                 with phi1_deg >= 0. 0 deg=horizon, +90 deg=zenith.
	 * @param h1_km (Optional) Height of atmospheric layer 1 (km). Default value is 0.
	 * @param hk_km (Optional) Height of atmospheric layer k (km). Default value is 100.1.
	 * @param atm (Optional) A reference atmosphere from ITU-R P.835-6.
	 *            Default value is MEAN_ANNUAL_GLOBAL.
	 * @param rho0_gm3 (Optional) Ground-level water vapour density (g/m3). Only applies when atm
	 *                 is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
	 * @return The downwelling atmospheric microwave brightness temperature, TB_downwelling (K).
	 */
	static double DownwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km = 0.0, double hk_km = 100.1, Atm atm = Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3 = 7.5);

	/**
	 * @brief ITU-R P.676-13, Annex 1, Section 4.2.
	 * 
	 * The upwelling atmospheric microwave brightness temperature (K).
	 * 
	 * @param f_GHz Frequency in GHz, with 1 <= f_GHz <= 1000.
	 * @param phi1_deg The local apparent elevation angle at height h1_km (degrees), 
	 *                 with phi1_deg >= 0. 0 deg=horizon, +90 deg=zenith.
	 * @param h1_km (Optional) Height of atmospheric layer 1 (km). Default value is 0.
	 * @param hk_km (Optional) Height of atmospheric layer k (km). Default value is 100.1.
	 * @param atm (Optional) A reference atmosphere from ITU-R P.835-6.
	 *            Default value is MEAN_ANNUAL_GLOBAL.
	 * @param rho0_gm3 (Optional) Ground-level water vapour density (g/m3). Only applies when atm
	 *                 is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
	 * @param emissivity (Optional) Emissivity of the Earth's surface. Default value is 0.95.
	 * @param TEarth_K (Optional) Temperature of the Earth's surface (K). Default value is 290.
	 * @return The upwelling atmospheric microwave brightness temperature, TB_upwelling (K).
	 */
	static double UpwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, double h1_km = 0.0, double hk_km = 100.1, Atm atm = Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3 = 7.5, double emissivity = 0.95, double TEarth_K = 290.0);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Section 1.1.
	 * 
	 * Gets the predicted slant path instantaneous gaseous attenuation attributable to oxygen (dB).
	 * The prediction method is applicable to paths between the surface of the Earth and space for
	 * elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param ps_hPa Instantaneous total (barometric) surface pressure (hPa) at the desired
	 *               location.
	 * @param Ts_K Instantaneous surface temperature (K) at the desired location.
	 * @param rhows_gm3 Instantaneous surface water vapour density (g/m3) at the desired
	 *                  location.
	 * @return The predicted slant path instantaneous gaseous attenuation attributable to
	 *         oxygen, Ao (dB).
	 */
	static double SlantPathInstantOxygenGaseousAtt(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Section 1.2.
	 * 
	 * Gets the predicted slant path statistical gaseous attenuation attributable to oxygen (dB).
	 * The prediction method is applicable to paths between the surface of the Earth and space for
	 * elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent <= 99
	 *                  for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511-3. Default value is AUTO.
	 * @return The predicted slant path statistical gaseous attenuation attributable to
	 *         oxygen, Ao (dB).
	 */
	static double SlantPathStatisticalOxygenGaseousAtt(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Section 2.1.
	 * 
	 * Gets the predicted slant path instantaneous gaseous attenuation attributable to water vapour,
	 * in dB, using method 1. The prediction method is applicable to paths between the surface of the
	 * Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
	 * 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param ps_hPa Instantaneous total (barometric) surface pressure (hPa) at the desired
	 *               location.
	 * @param Ts_K Instantaneous surface temperature (K) at the desired location.
	 * @param rhows_gm3 Instantaneous surface water vapour density (g/m3) at the desired
	 *                  location.
	 * @return The predicted slant path instantaneous gaseous attenuation attributable to
	 *         water vapour, Aw (dB).
	 */
	static double SlantPathInstantWaterVapourGaseousAtt1(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Section 2.2.
	 * 
	 * Gets the predicted slant path instantaneous gaseous attenuation attributable to water vapour,
	 * in dB, using method 2. The prediction method is applicable to paths between the surface of the
	 * Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
	 * 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param ps_hPa Instantaneous total (barometric) surface pressure (hPa) at the desired
	 *               location.
	 * @param Ts_K Instantaneous surface temperature (K) at the desired location.
	 * @param rhows_gm3 Instantaneous surface water vapour density (g/m3) at the desired
	 *                  location.
	 * @param Vs_kgm2 Integrated water vapour content (kg/m2 or mm) from the surface of the
	 *                Earth at the desired location.
	 * @return The predicted slant path instantaneous gaseous attenuation attributable to
	 *         water vapour, Aw (dB).
	 */
	static double SlantPathInstantWaterVapourGaseousAtt2(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3, double Vs_kgm2);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Section 2.3.
	 * 
	 * Gets the predicted slant path statistical gaseous attenuation attributable to water vapour (dB).
	 * The prediction method is applicable to paths between the surface of the Earth and space for
	 * elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent <= 99
	 *                  for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511-3. Default value is AUTO.
	 * @return The predicted slant path statistical gaseous attenuation attributable to water
	 *         vapour, Aw (dB).
	 */
	static double SlantPathStatisticalWaterVapourGaseousAtt(double f_GHz, double theta_deg, double p_percent, double lat, double lon,  int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Sections 1.1 and 2.1.
	 * 
	 * Gets the predicted slant path instantaneous gaseous attenuation attributable to both oxygen
	 * and water vapour (dB). The prediction method is applicable to paths between the surface of the
	 * Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
	 * 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param ps_hPa Instantaneous total (barometric) surface pressure (hPa) at the desired
	 *               location.
	 * @param Ts_K Instantaneous surface temperature (K) at the desired location.
	 * @param rhows_gm3 Instantaneous surface water vapour density (g/m3) at the desired
	 *                  location.
	 * @param Vs_kgm2 (Optional) Integrated water vapour content (kg/m2 or mm) from the
	 *                surface of the Earth at the desired location. When set to NONE, the prediction method
	 *                from Annex 2, Section 2.1 is used, otherwise the prediction method from Annex 2,
	 *                Section 2.2 is used. Default value is NONE.
	 * @return The predicted slant path instantaneous gaseous attenuation attributable to
	 *         both oxygen and water vapour, A_total (dB).
	 */
	static double SlantPathInstantGaseousAttenuation(double f_GHz, double theta_deg, double ps_hPa, double Ts_K, double rhows_gm3, double Vs_kgm2 = NONE);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Sections 1.2 and 2.3.
	 * 
	 * Gets the predicted slant path statistical gaseous attenuation attributable to both oxygen and
	 * water vapour (dB). The prediction method is applicable to paths between the surface of the
	 * Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
	 * 350 GHz.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent <= 99
	 *                  for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511-3. Default value is AUTO.
	 * @return The predicted slant path statistical gaseous attenuation attributable to
	 *         both oxygen and water vapour, A_total (dB).
	 */
	static double SlantPathStatisticalGaseousAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.676-13, Annex 2, Section 2.4.
	 * 
	 * Gets the Weibull approximation to the predicted slant path statistical gaseous attenuation
	 * attributable to water vapour (dB). This approximation is based on annual statistics.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 350.
	 * @param theta_deg Elevation angle (degrees), with 5 <= theta_deg <= 90.
	 * @param p_percent Exceedance probability (CCDF) of interest, in %.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511-3. Default value is AUTO.
	 * @return The Weibull approximation to the predicted slant path statistical gaseous
	 *         attenuation attributable to water vapour, Aw (dB).
	 */
	static double WeibullApproximation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, double h_mamsl = AUTO);

protected:
	static double NppOxygen(double f_GHz, double p_hPa, double T_K, double rho_gm3);
	static double NppWaterVapour(double f_GHz, double p_hPa, double T_K, double rho_gm3);
	static double RefractiveIndex(double h_km, Atm atm=Atm::MEAN_ANNUAL_GLOBAL, double rho0_gm3=7.5);
	static std::pair<int, int> LayerIndices(double h_lower, double h_upper);
	static double LayerThickness(int i, int i_lower, int i_upper, double h_lower, double h_upper);
	static double LayerBottomHeight(int i, int i_lower, int i_upper, double h_lower, double h_upper);
	static double NonNegElevAnglSlantPathGaseousAtt(double f_GHz, double h1_km, double h2_km, double phi1_deg, Atm atm, double rho0_gm3);
	static double NegElevAnglSlantPathGaseousAtt(double f_GHz, double h1_km, double h2_km, double phi1_deg, Atm atm, double rho0_gm3);
	static double NpOxygen(double f_GHz, double p_hPa, double T_K, double rho_gm3);
	static double NpWaterVapour(double f_GHz, double p_hPa, double T_K, double rho_gm3);
	static double TBFunc(double f_GHz, double Tj);
	static std::tuple<double, double, double, double> Part1Coeffs(double f_GHz);
	static std::tuple<double, double, double, double> Part2Coeffs(double f_GHz);
	static double SlantPathStatisticalOxygenGaseousAttHelper(double f_GHz, double theta_deg, double mean_ps_hPa, double mean_Ts_K, double mean_rhows_gm3, double psp_hPa, double Tsp_K, double rhowsp_gm3);
	static double SlantPathStatisticalWaterVapourGaseousAttHelper(double f_GHz, double theta_deg, double mean_ps_hPa, double mean_Ts_K, double mean_rhows_gm3, double Vsp_kgm2);
	static double WeibullApproximationHelper(double f_GHz, double theta_deg, double p_percent, double mean_ps_hPa, double mean_Ts_K, double mean_rhows_gm3, double lambda_VS, double k_VS);

	static constexpr int s_T1_ROW_COUNT = 44;
	static constexpr int s_T1_COL_COUNT = 7;
	static const double s_TABLE_1[s_T1_ROW_COUNT][s_T1_COL_COUNT];

	static constexpr int s_T2_ROW_COUNT = 35;
	static constexpr int s_T2_COL_COUNT = 7;
	static const double s_TABLE_2[s_T2_ROW_COUNT][s_T2_COL_COUNT];

	static const DigitalMap s_PART_1_COEFFS;
	static const DigitalMap s_PART_2_COEFFS;

private:
	// Prevent instantiation
	ITURP_676_13() = delete;
	ITURP_676_13(const ITURP_676_13&) = delete;
	ITURP_676_13(ITURP_676_13&&) = delete;
	ITURP_676_13& operator=(const ITURP_676_13&) = delete;
	ITURP_676_13& operator=(ITURP_676_13&&) = delete;
};