/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once


class ITURP_835_6
{
public:
	enum ReferenceAtmosphere : int
	{
		MEAN_ANNUAL_GLOBAL   = 1,
		LOW_LATITUDE         = 2,  // smaller than 22°
		MID_LATITUDE_SUMMER  = 3,  // between 22° and 45°
		MID_LATITUDE_WINTER  = 4,  // between 22° and 45°
		HIGH_LATITUDE_SUMMER = 5,  // higher than 45°
		HIGH_LATITUDE_WINTER = 6,  // higher than 45°
	};

	/**
	 * @brief Gets the atmospheric temperature (K) at geometric height h_km (km).
	 *
	 * ITU-R P.835-6, Annex 1.
	 *
	 * @param h_km Geometric height (km), with 0 <= h_km <= 100.
	 * @param atm  A reference atmosphere. Default value is MEAN_ANNUAL_GLOBAL.
	 *
	 * @return The atmospheric temperature (K) at geometric height h_km.
	 * 
	 * @throws std::invalid_argument If h_km is out of range or atm is not a valid value.
	 */
	static double Temperature(double h_km, ReferenceAtmosphere atm = MEAN_ANNUAL_GLOBAL);

	/**
	 * @brief Gets the total atmospheric pressure (hPa) at geometric height h_km (km).
	 *
	 * ITU-R P.835-6, Annex 1.
	 *
	 * @param h_km Geometric height (km), with 0 <= h_km <= 100.
	 * @param atm  A reference atmosphere. Default value is MEAN_ANNUAL_GLOBAL.
	 *
	 * @return The total atmospheric pressure (hPa) at geometric height h_km.
	 *
	 * @throws std::invalid_argument If h_km is out of range or atm is not a valid value.
	 */
	static double Pressure(double h_km, ReferenceAtmosphere atm = MEAN_ANNUAL_GLOBAL);

	/**
	 * @brief Gets the water-vapour density (g/m3) at geometric height h_km (km).
	 *
	 * ITU-R P.835-6, Annex 1.
	 *
	 * @param h_km     Geometric height (km), with 0 <= h_km <= 100.
	 * @param atm      A reference atmosphere. Default value is MEAN_ANNUAL_GLOBAL.
	 * @param rho0_gm3 Ground-level water vapour density (g/m3). Only applies when atm is set to
	 *                 MEAN_ANNUAL_GLOBAL. Default value is 7.5.
	 * @param h0_km    Scale height (km). Only applies when atm is set to MEAN_ANNUAL_GLOBAL.
	 *                 Default value is 2.
	 *
	 * @return The water-vapour density (g/m3) at geometric height h_km.
	 * 
	 * @throws std::invalid_argument If h_km is out of range or atm is not a valid value.
	 */
	static double WaterVapourDensity(double h_km, ReferenceAtmosphere atm = MEAN_ANNUAL_GLOBAL, double rho0_gm3 = 7.5, double h0_km = 2.0);

protected:
	static double GeometricToGeopotentialHeight(double h_km);
	static double GeopotentialToGeometricHeight(double hp_km);
	static double MagraPressure(double h);
	static double MagraTemperature(double h);
	static double LowLatTemperature(double h);
	static double LowLatPressure(double h);
	static double LowLatWaterVapourDensity(double h);
	static double SummerMidLatTemperature(double h);
	static double SummerMidLatPressure(double h);
	static double SummerMidLatWaterVapourDensity(double h);
	static double WinterMidLatTemperature(double h);
	static double WinterMidLatPressure(double h);
	static double WinterMidLatWaterVapourDensity(double h);
	static double SummerHighLatTemperature(double h);
	static double SummerHighLatPressure(double h);
	static double SummerHighLatWaterVapourDensity(double h);
	static double WinterHighLatTemperature(double h);
	static double WinterHighLatPressure(double h);
	static double WinterHighLatWaterVapourDensity(double h);

private:
	// Prevent instantiation
	ITURP_835_6() = delete;
	ITURP_835_6(const ITURP_835_6&) = delete;
	ITURP_835_6(ITURP_835_6&&) = delete;
	ITURP_835_6& operator=(const ITURP_835_6&) = delete;
	ITURP_835_6& operator=(ITURP_835_6&&) = delete;
};
