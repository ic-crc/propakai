/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <array>
#include <vector>
#include <string>
#include <unordered_map>
#include "DigitalMap.h"


class ITURP_840_9
{
public:
	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 1.
	 * 
	 * Gets the specific attenuation within a cloud or fog (dB/km).
	 * 
	 * "At frequencies of the order of 100 GHz and above, attenuation due to fog may be significant".
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 200.
	 * @param T_K Liquid water temperature (K).
	 * @param rhol_gm3 Liquid water density in the cloud or fog (g/m3). "Typically about 0.05
	 *                 g/m3 for medium fog (visibility of the order of 300 m) and 0.5 g/m3 for thick fog
	 *                 (visibility of the order of 50 m)."
	 * @return Specific attenuation, gamma_c (dB/km), within cloud or fog.
	 */
	static double CloudOrFogAttenuation(double f_GHz, double T_K, double rhol_gm3);

	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 2.
	 * 
	 * Gets the cloud liquid water specific attenuation coefficient (dB/km)/(g/m3).
	 * 
	 * @param f_GHz Frequency (GHz), with 1 <= f_GHz <= 200.
	 * @param T_K Liquid water temperature (K).
	 * @return The cloud liquid water specific attenuation coefficient, Kl ((dB/km)/(g/m3)).
	 */
	static double CloudLiquidWaterAttenuationCoefficient(double f_GHz, double T_K);

	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 3.1.
	 * 
	 * Gets the predicted slant path instantaneous cloud attenuation (dB).
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 200.
	 * @param theta_deg Elevation angle (degrees).
	 * @param L_kgm2 Integrated cloud liquid water content, in kg/m2 or mm, from the surface
	 *               of the Earth at the desired location.
	 * @return The predicted slant path instantaneous cloud attenuation, Ac (dB).
	 */
	static double SlantPathInstantaneousCloudAttenuation(double f_GHz, double theta_deg, double L_kgm2);

	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 3.2.
	 * 
	 * Gets the predicted slant path statistical cloud attenuation (dB).
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 200.
	 * @param theta_deg Elevation angle (degrees).
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
	 *                  <= 100 for annual statistics and with 0.1 <= p_percent <= 100 for monthly statistics.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @return The predicted slant path statistical cloud attenuation, Ac (dB).
	 */
	static double SlantPathStatisticalCloudAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon, int month = -1);
	
	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 3.3.
	 * 
	 * Gets the log-normal approximation to the predicted slant path statistical cloud
	 * attenuation (dB). Uses annual statistics.
	 * 
	 * @param f_GHz Frequency of interest (GHz), with 1 <= f_GHz <= 200.
	 * @param theta_deg Elevation angle (degrees).
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent <= 100.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @return The log-normal approximation to the predicted slant path statistical cloud
	 *         attenuation, Ac (dB).
	 */
	static double LogNormalApproxToStatCloudAttenuation(double f_GHz, double theta_deg, double p_percent, double lat, double lon);

	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 4.
	 * 
	 * Gets the integrated cloud liquid water content for the provided exceedance probability, in
	 * kg/m2, or, equivalently, mm.
	 * 
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
	 *                  <= 100 for annual statistics and with 0.1 <= p_percent <= 100 for monthly statistics.
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @return The integrated cloud liquid water content, L, in kg/m2, or, equivalently, mm.
	 */
	static double IntegratedCloudLiquidWaterContent(double p_percent, double lat, double lon, int month = -1);

	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 4.
	 * 
	 * Gets the mean of the integrated cloud liquid water content.
	 * 
	 * @param lat Latitude of the desired location (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (degrees), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @return The mean of the integrated cloud liquid water content, L_mean.
	 */
	static double MeanIntegratedCloudLiquidWaterContent(double lat, double lon, int month = -1);

	/**
	 * @brief ITU-R P.840-9, Annex 1, Section 4.
	 * 
	 * Gets the standard deviation of the integrated cloud liquid water content.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @return The standard deviation of the integrated cloud liquid water content, L_std.
	 */
	static double StdDevIntegratedCloudLiquidWaterContent(double lat, double lon, int month = -1);

protected:
	static const DigitalMap& GetDigitalMap(int month, const std::string& filenameNoExt);
	static double KL(double f_GHz);

	struct PFile
	{
		double p;
		std::string filenameNoExt;
	};

	static const std::vector<PFile> s_ANNUAL_P_FILES;
	static const std::vector<PFile> s_MONTHLY_P_FILES;
	static const std::array<std::string, 12> s_MONTH_FOLDERS;

	static const std::unordered_map<std::string, DigitalMap> s_Annual_maps;
	static const std::unordered_map<std::string, DigitalMap> s_Monthly_maps;

private:
	// Prevent instantiation
	ITURP_840_9() = delete;
	ITURP_840_9(const ITURP_840_9&) = delete;
	ITURP_840_9(ITURP_840_9&&) = delete;
	ITURP_840_9& operator=(const ITURP_840_9&) = delete;
	ITURP_840_9& operator=(ITURP_840_9&&) = delete;
};
