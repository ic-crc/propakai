/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <vector>
#include <utility>
#include "DigitalMap.h"
#include <array>

class ITURP_837_8
{
public:
	/**
	 * @brief Gets the annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
	 * 
	 * @details ITU-R P.837-8. This function uses bilinear interpolation on the precalculated R001.txt file.
	 * 
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @return The annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
	 */
	static double AnnualRainfallRate001(double lat, double lon);

	/**
	 * @brief Gets the total monthly mean rainfall (mm).
	 * 
	 * @details ITU-R P.837-8, Annex 1.
	 * 
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @param month Month (1=Jan, ..., 12=Dec).
	 * @return Total monthly mean rainfall (mm).
	 */
	static double TotalMonthlyMeanRainfall(double lat, double lon, int month);

	/**
	 * @brief Gets the rainfall rate at the desired annual rainfall rate probability of exceedance (mm/hr),
	 * along with the annual probability of rain (%).
	 * 
	 * @details ITU-R P.837-8, Annex 1.
	 * 
	 * @param p_percent Annual rainfall rate probability of exceedance (%).
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @return 
	 * - first (Rp): Rainfall rate exceeded for the desired annual probability of exceedance, p_percent,
	 *   at the specified location on the surface of the Earth, and for an integration time of 1 minute (mm/hr).
	 * - second (P0_annual): Annual probability of rain (%).
	 */
	static std::pair<double, double> AnnualRainfallRate(double p_percent, double lat, double lon);

	/**
	 * @brief Gets the annual probability of rain (%).
	 *
	 * @details ITU-R P.837-8, Annex 1.
	 *
	 * @param lat Latitude (degrees), with -90.0 <= lat <= 90.0.
	 * @param lon Longitude (degrees), with -180.0 <= lon <= 180.0.
	 * @return Annual probability of rain (%).
	 */
	static double AnnualProbabilityOfRain(double lat, double lon);

	/**
	 * @brief Gets the rainfall rate at the desired monthly rainfall rate probability of exceedance (mm/hr),
	 * along with the monthly probability of rain (%).
	 * 
	 * @details ITU-R P.837-8, Annex 1.
	 * 
	 * @param p_percent Monthly rainfall rate probability of exceedance (%).
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @param month Month (1=Jan, ..., 12=Dec).
	 * @return
	 * - first (Rp_ii): Rainfall rate exceeded for the desired monthly probability of exceedance, p_percent,
	 *   at the specified location on the surface of the Earth, and for an integration time of 1 minute (mm/hr).
	 * - second (P0_ii): Monthly probability of rain (%).
	 */
	static std::pair<double, double> MonthlyRainfallRate(double p_percent, double lat, double lon, int month);

	/**
	 * @brief Gets the monthly probability of rain (%) for the specified month.
	 *
	 * @details ITU-R P.837-8, Annex 1.
	 *
	 * @param lat Latitude (degrees), with -90.0 <= lat <= 90.0.
	 * @param lon Longitude (degrees), with -180.0 <= lon <= 180.0.
	 * @return Monthly probability of rain (%).
	 */
	static double MonthlyProbabilityOfRain(double lat, double lon, int month);

protected:
	static double Q(double x);

	static const DigitalMap s_R001_map;
	static const std::vector<DigitalMap> s_MT_Month_maps;

	static constexpr std::array<double, 12> s_DaysPerMonth = {
		31.0, 28.25, 31.0, 30.0, 31.0, 30.0, 31.0, 31.0, 30.0, 31.0, 30.0, 31.0
	};

private:
	// Prevent instantiation
	ITURP_837_8() = delete;
	ITURP_837_8(const ITURP_837_8&) = delete;
	ITURP_837_8(ITURP_837_8&&) = delete;
	ITURP_837_8& operator=(const ITURP_837_8&) = delete;
	ITURP_837_8& operator=(ITURP_837_8&&) = delete;
};