/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once


class ITURP_835_7
{
public:
	enum ReferenceAtmosphere : int
	{
		ITU_R           = 1,
		SEASONAL_SUMMER = 2,
		SEASONAL_WINTER = 3
	};

	/**
	 * @brief Gets the atmospheric temperature (K) at geometric height z_km (km).
	 *
	 * ITU-R P.835-7, Annex 1 & 2.
	 *
	 * @param z_km Geometric height (km), with 0 <= z_km <= 100.
	 * @param atm  A reference atmosphere (ITU_R, SEASONAL_SUMMER or SEASONAL_WINTER). Default value
	 *             is ITU_R.
	 * @param lat  Latitude (degrees), with -90 <= lat <= 90. Unused when atm is set to ITU_R.
	 *             Default value is 45.
	 *
	 * @return The atmospheric temperature (K) at geometric height z_km.
	 *
	 * @throws std::invalid_argument If z_km is out of range.
	 */
	static double Temperature(double z_km, ReferenceAtmosphere atm = ITU_R, double lat = 45.0);


	/**
	 * @brief Gets the total (barometric) atmospheric pressure (hPa) at geometric height z_km (km).
	 *
	 * ITU-R P.835-7, Annex 1 & 2.
	 *
	 * @param z_km Geometric height (km), with 0 <= z_km <= 100.
	 * @param atm  A reference atmosphere (ITU_R, SEASONAL_SUMMER or SEASONAL_WINTER). Default value
	 *             is ITU_R.
	 * @param lat  Latitude (degrees), with -90 <= lat <= 90. Unused when atm is set to ITU_R.
	 *             Default value is 45.
	 *
	 * @return The total (barometric) atmospheric pressure (hPa) at geometric height z_km.
	 *
	 * @throws std::invalid_argument If z_km is out of range.
	 */
	static double Pressure(double z_km, ReferenceAtmosphere atm = ITU_R, double lat = 45.0);

	/**
	 * @brief Gets the atmospheric water vapour density (g/m3) at geometric height z_km (km).
	 *
	 * ITU-R P.835-7, Annex 1 & 2.
	 *
	 * @param z_km Geometric height (km), with 0 <= z_km <= 100.
	 * @param atm  A reference atmosphere (ITU_R, SEASONAL_SUMMER or SEASONAL_WINTER). Default value
	 *             is ITU_R.
	 * @param lat  Latitude (degrees), with -90 <= lat <= 90. Unused when atm is set to ITU_R.
	 *             Default value is 45.
	 *
	 * @return The water-vapour density (g/m3) at geometric height z_km.
	 *
	 * @throws std::invalid_argument If z_km is out of range.
	 */
	static double WaterVapourDensity(double z_km, ReferenceAtmosphere atm = ITU_R, double lat = 45.0);

protected:
	static double GeometricToGeopotentialHeight(double z_km);
	static double GeopotentialToGeometricHeight(double h_km);
	static double ItuRTemperature(double z_km);
	static double ItuRPressure(double z_km);
	static double LowLatTemperature(double z_km);
	static double LowLatPressure(double z_km);
	static double LowLatWaterVapourDensity(double z_km);
	static double SummerMidLatTemperature(double z_km);
	static double SummerMidLatPressure(double z_km);
	static double SummerMidLatWaterVapourDensity(double z_km);
	static double WinterMidLatTemperature(double z_km);
	static double WinterMidLatPressure(double z_km);
	static double WinterMidLatWaterVapourDensity(double z_km);
	static double SummerHighLatTemperature(double z_km);
	static double SummerHighLatPressure(double z_km);
	static double SummerHighLatWaterVapourDensity(double z_km);
	static double WinterHighLatTemperature(double z_km);
	static double WinterHighLatPressure(double z_km);
	static double WinterHighLatWaterVapourDensity(double z_km);
	static double SeasonalInterpolate(double z_km, ReferenceAtmosphere seasonal_atm, double lat,
	                                  double (*lowLatFunc)(double), double (*summerMidLatFunc)(double),
	                                  double (*winterMidLatFunc)(double), double (*summerHighLatFunc)(double),
	                                  double (*winterHighLatFunc)(double));

private:
	// Prevent instantiation
	ITURP_835_7() = delete;
	ITURP_835_7(const ITURP_835_7&) = delete;
	ITURP_835_7(ITURP_835_7&&) = delete;
	ITURP_835_7& operator=(const ITURP_835_7&) = delete;
	ITURP_835_7& operator=(ITURP_835_7&&) = delete;
};
