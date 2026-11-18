/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <limits>


class ITURP_2108_1
{
public:
	enum ClutterCategory : int
	{
		WATER_SEA           = 1,
		OPEN_RURAL          = 2,
		SUBURBAN            = 3,
		URBAN_TREES_FOREST  = 4,
		DENSE_URBAN         = 5
	};

	static constexpr double AUTO = std::numeric_limits<double>::quiet_NaN();

	/**
	 * @brief ITU-R P.2108-1, Annex 1, Section 3.1.
	 * 
	 * Gets the additional loss (dB) from the height gain terminal correction model.
	 * 
	 * "An additional loss, Ah, is calculated which can be added to the basic transmission loss of a
	 * path calculated above the clutter, therefore basic transmission loss should be calculated
	 * to/from the height of the representative clutter height used. This model can be applied to both
	 * transmitting and receiving ends of the path."
	 * 
	 * @param f_GHz Frequency (GHz), with 0.03 <= f_GHz <= 3.
	 * @param h_m Antenna height (m), with 0 <= h_m.
	 * @param clut One of the clutter types from the recommendation's Table 3.
	 * @param R_m (Optional) Representative clutter height (m), with 0 < R_m. When R_m is
	 *            set to AUTO, the default representative clutter height for the specified clutter type
	 *            is used. Default value is AUTO.
	 * @param ws_m (Optional) Street width (m). Default value is 27.
	 * @return Additional loss, Ah (dB).
	 */
	static double HeightGainTerminalCorrection(double f_GHz, double h_m, ITURP_2108_1::ClutterCategory clut, double R_m=AUTO, double ws_m=27.0);

	/**
	 * @brief ITU-R P.2108-1, Annex 1, Section 3.2.
	 * 
	 * "Statistical model which can be applied for modelling the clutter loss distribution for urban
	 * and suburban environments." Terminal heights are assumed to be well below the clutter height.
	 * 
	 * @param f_GHz Frequency (GHz), with 0.5 <= f_GHz <= 67.
	 * @param d_km Distance (km), with 0.25 <= d_km.
	 * @param p_percent Percentage of locations (%), with 0 < p_percent < 100.
	 * @return Median clutter loss for terrestrial paths, Lctt (dB).
	 */
	static double TerrestrialPathClutterLoss(double f_GHz, double d_km, double p_percent);

	/**
	 * @brief ITU-R P.2108-1, Annex 1, Section 3.3.
	 * 
	 * "Statistical distribution of clutter loss where one end of the interference path is within
	 * man-made clutter, and the other is a satellite, aeroplane, or other platform above the surface
	 * of the Earth." "This model is applicable to urban and suburban environments."
	 * 
	 * @param f_GHz Frequency (GHz), with 0.5 <= f_GHz <= 67.
	 * @param theta_deg Elevation angle (degrees). The angle of the airborne platform or
	 *                  satellite as seen from the terminal, with 0 <= theta_deg <= 90.
	 * @param p_percent Percentage of locations (%), with 0 < p_percent < 100.
	 * @return Additional clutter loss, Lces (dB), "which can be added to the basic transmission
	 *         loss of a path calculated."
	 */
	static double EarthSpaceClutterLoss(double f_GHz, double theta_deg, double p_percent);

private:
	// Prevent instantiation
	ITURP_2108_1() = delete;
	ITURP_2108_1(const ITURP_2108_1&) = delete;
	ITURP_2108_1(ITURP_2108_1&&) = delete;
	ITURP_2108_1& operator=(const ITURP_2108_1&) = delete;
	ITURP_2108_1& operator=(ITURP_2108_1&&) = delete;
};
