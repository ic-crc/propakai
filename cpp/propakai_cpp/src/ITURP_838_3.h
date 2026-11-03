/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <array>


class ITURP_838_3
{
public:
	struct Coeffs {
		double k;
		double alpha;
	};

	/**
	* @brief ITU-R P.838-3: Attenuation due to rain (dB/km).
	* 
	* @param f_Ghz Frequency (GHz), with 1 <= f_Ghz <= 1000.
	* @param R_mmhr Rain rate (mm/hr).
	* @param theta_degrees Path elevation angle (degrees).
	* @param tau_degrees Polarization tilt angle relative to the horizontal (degrees). 
	*                    Use 45 deg for circular polarization.
	* @return Attenuation due to rain, gamma_R (dB/km).
	*/
	static double RainAttenuation(double f_Ghz, double R_mmhr, double theta_degrees, double tau_degrees);

	/**
	* @brief ITU-R P.838-3: Gets the coefficients k and alpha from equations (4) and (5).
	* 
	* @param f_Ghz Frequency (GHz), with 1 <= f_Ghz <= 1000.
	* @param theta_degrees Path elevation angle (degrees).
	* @param tau_degrees Polarization tilt angle relative to the horizontal (degrees). 
	*                    Use 45 deg for circular polarization.
	* @return Coeffs struct containing coefficient k and coefficient alpha.
	*/
	static Coeffs Coefficients(double f_Ghz, double theta_degrees, double tau_degrees);

protected:
	static double KH(double f_Ghz);
	static double KV(double f_Ghz);
	static double AH(double f_Ghz);
	static double AV(double f_Ghz);
	static double PolK(double f_Ghz, const std::array<double, 4>& a, const std::array<double, 4>& b, const std::array<double, 4>& c, double mk, double ck);
	static double PolAlpha(double f_Ghz, const std::array<double, 5>& a, const std::array<double, 5>& b, const std::array<double, 5>& c, double ma, double ca);

private:
	// Prevent instantiation
	ITURP_838_3() = delete;                                // Delete default constructor
	ITURP_838_3(const ITURP_838_3&) = delete;              // Delete copy constructor
	ITURP_838_3(ITURP_838_3&&) = delete;                   // Delete move constructor
	ITURP_838_3& operator=(const ITURP_838_3&) = delete;   // Delete copy assignment
	ITURP_838_3& operator=(ITURP_838_3&&) = delete;        // Delete move assignment
};
