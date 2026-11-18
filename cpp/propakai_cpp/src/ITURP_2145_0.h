/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <string>
#include <array>
#include <vector>
#include <unordered_map>
#include <limits>
#include "DigitalMap.h"


class ITURP_2145_0
{
public:
	static constexpr double AUTO = std::numeric_limits<double>::quiet_NaN();

	/**
	 * @brief ITU-R P.2145-0, Section 2.1 of Annex.
	 * 
	 * Gets the surface total (barometric) pressure (hPa) for the specified exceedance probability
	 * p_percent (CCDF - complementary cumulative distribution function) at the specified location on
	 * the surface of the Earth.
	 * 
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
	 *                  <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The surface total (barometric) pressure, P (hPa), for the specified exceedance
	 *         probability p_percent (CCDF) at the specified location on the surface of the Earth.
	 */
	static double SurfaceTotalPressure(double p_percent, double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.1 of Annex.
	 * 
	 * Gets the surface temperature (K) for the specified exceedance probability p_percent (CCDF - 
	 * complementary cumulative distribution function) at the specified location on the surface of the
	 * Earth.
	 * 
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
	 *                  <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The surface temperature, T (K), for the specified exceedance probability p_percent
	 *         (CCDF) at the specified location on the surface of the Earth.
	 */
	static double SurfaceTemperature(double p_percent, double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.1 of Annex.
	 * 
	 * Gets the surface water vapour density (g/m3) for the specified exceedance probability p_percent
	 * (CCDF - complementary cumulative distribution function) at the specified location on the
	 * surface of the Earth.
	 * 
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
	 *                  <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The surface water vapour density, rho (g/m3), for the specified exceedance
	 *         probability p_percent (CCDF) at the specified location on the surface of the Earth.
	 */
	static double SurfaceWaterVapourDensity(double p_percent, double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.1 of Annex.
	 * 
	 * Gets the integrated water vapour content (kg/m2) for the specified exceedance probability
	 * p_percent (CCDF - complementary cumulative distribution function) at the specified location on
	 * the surface of the Earth.
	 * 
	 * @param p_percent Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
	 *                  <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The integrated water vapour content, V (kg/m2), for the specified exceedance
	 *         probability p_percent (CCDF) at the specified location on the surface of the Earth.
	 */
	static double IntegratedWaterVapourContent(double p_percent, double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the mean of the surface total (barometric) pressure (hPa) at the specified location on the 
	 * surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The mean of the surface total (barometric) pressure (hPa) at the specified location
	 *         on the surface of the Earth.
	 */
	static double MeanSurfaceTotalPressure(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the mean of the surface temperature (K) at the specified location on the surface of the
	 * Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The mean of the surface temperature (K) at the specified location on the surface
	 *         of the Earth.
	 */
	static double MeanSurfaceTemperature(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the mean of the surface water vapour density (g/m3) at the specified location on the
	 * surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The mean of the surface water vapour density (g/m3) at the specified location on
	 *         the surface of the Earth.
	 */
	static double MeanSurfaceWaterVapourDensity(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the mean of the integrated water vapour content (kg/m2) at the specified location on the 
	 * surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The mean of the integrated water vapour content (kg/m2) at the specified location
	 *         on the surface of the Earth.
	 */
	static double MeanIntegratedWaterVapourContent(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the standard deviation of the surface total (barometric) pressure (hPa) at the specified
	 * location on the surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The standard deviation of the surface total (barometric) pressure (hPa) at the
	 *         specified location on the surface of the Earth.
	 */
	static double StdDevSurfaceTotalPressure(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the standard deviation of the surface temperature (K) at the specified location on the
	 * surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The standard deviation of the surface temperature (K) at the specified location on
	 *         the surface of the Earth.
	 */
	static double StdDevSurfaceTemperature(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the standard deviation of the surface water vapour density (g/m3) at the specified
	 * location on the surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The standard deviation of the surface water vapour density (g/m3) at the specified
	 *         location on the surface of the Earth.
	 */
	static double StdDevSurfaceWaterVapourDensity(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the standard deviation of the integrated water vapour content (kg/m2) at the specified
	 * location on the surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param month (Optional) Month to get the statistics for (1=Jan, ..., 12=Dec). Use
	 *              -1 for annual statistics. Default value is -1.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The standard deviation of the integrated water vapour content (kg/m2) at the
	 *         specified location on the surface of the Earth.
	 */
	static double StdDevIntegratedWaterVapourContent(double lat, double lon, int month = -1, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the Weibull integrated water vapour content shape parameter at the specified
	 * location on the surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The Weibull integrated water vapour content shape parameter, k_VS.
	 */
	static double WeibullShapeParameter(double lat, double lon, double h_mamsl = AUTO);

	/**
	 * @brief ITU-R P.2145-0, Section 2.2 of Annex.
	 * 
	 * Gets the Weibull integrated water vapour content scale parameter at the specified
	 * location on the surface of the Earth.
	 * 
	 * @param lat Latitude of the desired location (deg), with -90 <= lat <= 90.
	 * @param lon Longitude of the desired location (deg), with -180 <= lon <= 180.
	 * @param h_mamsl (Optional) Height of the desired location (meters above mean sea
	 *                level). When set to AUTO, the height is automatically obtained from Recommendation
	 *                ITU-R P.1511. Default value is AUTO.
	 * @return The Weibull integrated water vapour content scale parameter, lambda_VS.
	 */
	static double WeibullScaleParameter(double lat, double lon, double h_mamsl = AUTO);

protected:
	struct NominalProb
	{
		double p;
		std::string pStr;
	};

	static const std::vector<NominalProb> s_ANNUAL_NOMINAL_PROBS;
	static const std::vector<NominalProb> s_MONTHLY_NOMINAL_PROBS;
	static const std::array<std::string, 12> s_MONTH_FOLDERS;
	static const std::array<std::string, 4> s_PARAMS;

	static const std::unordered_map<std::string, DigitalMap> s_Annual_maps;
	static const std::unordered_map<std::string, DigitalMap> s_Monthly_maps;

	struct CCDFMaps
	{
		const double pBelow;
		const DigitalMap& pBelowMap;
		const double pAbove;
		const DigitalMap& pAboveMap;
		const DigitalMap& schMap;
		const DigitalMap& zMap;
	};
	static CCDFMaps GetCCDFMaps(double p_percent, int month, const std::string& param);

	struct MeanStdDevMaps
	{
		const DigitalMap& meanMap;
		const DigitalMap& stdDevMap;
		const DigitalMap& schMap;
		const DigitalMap& zMap;
	};
	static MeanStdDevMaps GetMeanStdDevMaps(int month, const std::string& param);

	using ScalingFunc = double (*)(double, double, double, double);
	static double CCDFInterpolation(double p_percent, double lat, double lon, double h_mamsl, const CCDFMaps& maps, ScalingFunc scalingFunc);
	static double MeanStdDevInterpolation(double lat, double lon, double h_mamsl, const DigitalMap& mainMap, const DigitalMap& schMap, const DigitalMap& zMap, ScalingFunc scalingFunc);

    static double ExpScalingFunc(double xp, double sch, double alt, double alti);
	static double AddScalingFunc(double xp, double sch, double alt, double alti);
	static double DirectScalingFunc(double xp, double /*sch*/, double /*alt*/, double /*alti*/);

private:
	// Prevent instantiation
	ITURP_2145_0() = delete;
	ITURP_2145_0(const ITURP_2145_0&) = delete;
	ITURP_2145_0(ITURP_2145_0&&) = delete;
	ITURP_2145_0& operator=(const ITURP_2145_0&) = delete;
	ITURP_2145_0& operator=(ITURP_2145_0&&) = delete;
};
