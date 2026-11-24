/*
 * Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_676_13.h"
#include <cmath>
#include <algorithm>
#include <cstddef>
#include <utility> // for std::pair
#include <tuple>
#include "ITURP_835_6.h"
#include "ITURP_2145_0.h"
#include "ITURP_1511_3.h"


double ITURP_676_13::GaseousAttenuation(double f_GHz, double p_hPa/*=1013.25*/, double T_K/*=288.15*/, double rho_gm3/*=7.5*/)
{
    const double gamma_o = DryAirGaseousAttenuation(f_GHz, p_hPa, T_K, rho_gm3);
    const double gamma_w = WaterVapourGaseousAttenuation(f_GHz, p_hPa, T_K, rho_gm3);
    return gamma_o+gamma_w;
}

double ITURP_676_13::DryAirGaseousAttenuation(double f_GHz, double p_hPa/*=1013.25*/, double T_K/*=288.15*/, double rho_gm3/*=7.5*/)
{
	return 0.1820*f_GHz*NppOxygen(f_GHz, p_hPa, T_K, rho_gm3);
}

double ITURP_676_13::WaterVapourGaseousAttenuation(double f_GHz, double p_hPa/*=1013.25*/, double T_K/*=288.15*/, double rho_gm3/*=7.5*/)
{
	return 0.1820*f_GHz*NppWaterVapour(f_GHz, p_hPa, T_K, rho_gm3);
}

// ITU-R P.676-13, Annex 1, Section 1.
// 
// N''Oxygen.
// 
// f_GHz: Frequency (GHz), with 1 <= f_GHz <= 1000.
// p_hPa: Atmospheric pressure (hPa).
// T_K: Temperature (K).
// rho_gm3: Water vapour density (g/m3).
// Returns: Imaginary part of the complex refractivity attributable to oxygen.
double ITURP_676_13::NppOxygen(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	const double theta = 300.0/T_K;
	const double e = rho_gm3*T_K/216.7;
	double NppO = 0.0;

	const double prod1 = 1.0E-7*p_hPa*theta*theta*theta;
	const double prod2 = 1.1*e*theta;
	const double prod3 = 1.0E-4*(p_hPa+e)*std::pow(theta,0.8);

	for(int i=0 ; i<s_T1_ROW_COUNT ; ++i)
	{
		const double fi = s_TABLE_1[i][0];
		const double* a = s_TABLE_1[i];

		const double Si = a[1] * prod1 * std::exp(a[2]*(1.0-theta));

		const double df_ = a[3]*1.0E-4*((p_hPa*std::pow(theta,0.8-a[4]))+prod2);
		const double df = std::sqrt((df_*df_)+2.25E-6);
		const double delta = (a[5]+(a[6]*theta))*prod3;

		const double Fi = (f_GHz/fi)*( ((df-(delta*(fi-f_GHz)))/(((fi-f_GHz)*(fi-f_GHz))+(df*df))) +
		                  ((df-(delta*(fi+f_GHz)))/(((fi+f_GHz)*(fi+f_GHz))+(df*df))) );
		
		NppO += Si*Fi;
	}

	const double d = 5.6E-4*(p_hPa+e)*std::pow(theta, 0.8);
	const double NppD = f_GHz*p_hPa*theta*theta*( (6.14E-5/(d*(1.0+((f_GHz*f_GHz)/(d*d))))) +
	                    ((1.4E-12*p_hPa*std::pow(theta,1.5))/(1.0+(1.9E-5*std::pow(f_GHz,1.5)))) );
	NppO += NppD;

	return NppO;
}

// ITU-R P.676-13, Annex 1, Section 1.
// 
// N''Water Vapour.
// 
// f_GHz: Frequency (GHz), with 1 <= f_GHz <= 1000.
// p_hPa: Atmospheric pressure (hPa).
// T_K: Temperature (K).
// rho_gm3: Water vapour density (g/m3).
// Returns: Imaginary part of the complex refractivity attributable to water vapour.
double ITURP_676_13::NppWaterVapour(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	const double theta = 300.0/T_K;
	const double e = rho_gm3*T_K/216.7;
	double NppWV = 0.0;

	const double prod1 = 1.0E-1*e*std::pow(theta, 3.5);

	for(int i=0 ; i<s_T2_ROW_COUNT ; i++)
	{
		const double fi = s_TABLE_2[i][0];
		const double* b = s_TABLE_2[i];

		const double Si = b[1] * prod1 * std::exp(b[2]*(1.0-theta));

		const double df_ = b[3]*1.0E-4*((p_hPa*std::pow(theta,b[4])) + (b[5]*e*std::pow(theta,b[6])));
		const double df = 0.535*df_ + std::sqrt((0.217*df_*df_)+(2.1316E-12*fi*fi/theta));
		const double Fi = (f_GHz/fi)*( (df/(((fi-f_GHz)*(fi-f_GHz))+(df*df))) + (df/(((fi+f_GHz)*(fi+f_GHz))+(df*df))) );
		
		NppWV += Si*Fi;
	}

	return NppWV;
}

// ITU-R P.676-13, Annex 1, Section 2.2.1.
// 
// Calculates the atmospheric radio refractive index at any height for Earth-satellite paths.
// 
// h_km: Height in km, with h_km >= 0.
// atm: (Optional) A reference atmosphere from ITU-R P.835-6.
//      Default value is MEAN_ANNUAL_GLOBAL.
// rho0_gm3: (Optional) Ground-level water vapour density (g/m3). Only applies when atm
//           is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
// Returns: The radio refractive index, n, at height h_km (for Earth-satellite paths).
double ITURP_676_13::RefractiveIndex(double h_km, Atm atm, double rho0_gm3)
{
	// Outer space conventionally starts at 100 km above sea level.
	// See Section 2.2.3 of Annex 1 from ITU-R P.676-13.
	if (h_km > 100.0)
		return 1.0;

	// Extract from ITU-R P.453-14:
	// "For Earth-satellite paths, the refractive index at any height is obtained using equations
	// (1), (2) and (10) above, together with the appropriate values for the parameters given in
	// Recommendation ITU-R P.835, Annex 1."

	const double P = ITURP_835_6::Pressure(h_km, atm); // total atmospheric pressure (hPa)
	const double T = ITURP_835_6::Temperature(h_km, atm);
	const double rho = ITURP_835_6::WaterVapourDensity(h_km, atm, rho0_gm3);
	const double e = rho * T / 216.7; // water vapour pressure, in hPa. eq. (10) of P.453-14
	const double Pd = P - e; // dry atmospheric pressure (hPa). eq. (5) of P.453-14
	const double N = (77.6 * Pd / T) + (72.0 * e / T) + (3.75E5 * e / (T * T)); // eq. (2) of P.453-14
	const double n = 1.0 + (N * 1E-6); // eq. (1) of P.453-14
	return n;
}

// ITU-R P.676-13, Section 2.2.1 of Annex 1
std::pair<int, int> ITURP_676_13::LayerIndices(double h_lower, double h_upper)
{
	h_lower = std::max(0.0, h_lower);
	h_upper = std::min(100.0, h_upper);

	const double exp_term = std::expm1(0.01); // does "std::exp(0.01) - 1.0" avoiding precision loss

	int i_lower = static_cast<int>(std::floor(100.0 * std::log(1E4 * h_lower * exp_term + 1.0) + 1.0));
	int i_upper = static_cast<int>(std::ceil(100.0 * std::log(1E4 * h_upper * exp_term + 1.0) + 1.0));

	return {i_lower, i_upper};
}

// ITU-R P.676-13, Section 2.2.1 of Annex 1
double ITURP_676_13::LayerThickness(int i, int i_lower, int i_upper, double h_lower, double h_upper)
{
	double delta_i_km;

	if (h_lower == 0.0 && h_upper > 100.0)
		delta_i_km = 0.0001 * std::exp((i - 1) / 100.0);
	else
	{
		double m = ((std::exp(0.02) - std::exp(0.01)) / 
		            (std::exp(i_upper / 100.0) - std::exp(i_lower / 100.0))) * (h_upper - h_lower);
		delta_i_km = m * std::exp((i - 1) / 100.0);
	}

	return delta_i_km;
}

// ITU-R P.676-13, Section 2.2.1 of Annex 1
double ITURP_676_13::LayerBottomHeight(int i, int i_lower, int i_upper, double h_lower, double h_upper)
{
	double h_i_km;

	if (h_lower == 0.0 && h_upper > 100.0)
		h_i_km = 0.0001 * ((std::exp((i - 1) / 100.0) - 1.0) / (std::exp(0.01) - 1.0));
	else
	{
		double m = ((std::exp(0.02) - std::exp(0.01)) / 
					(std::exp(i_upper / 100.0) - std::exp(i_lower / 100.0))) * (h_upper - h_lower);
		h_i_km = h_lower + m * ((std::exp((i - 1) / 100.0) - std::exp((i_lower - 1) / 100.0)) / 
								(std::exp(0.01) - 1.0));
	}

	return h_i_km;
}

// ITU-R P.676-13, Annex 1, Section 2.2.1 (Non-negative apparent elevation angles).
// 
// Calculates the Earth-space slant path gaseous attenuation for an ascending path between a
// location on or near the surface of the Earth and a location above the surface of the Earth or
// in space.
// 
// f_GHz: Frequency in GHz, with 1 <= f_GHz <= 1000.
// h1_km: Height of the first station (km), with 0 <= h1_km < h2_km.
// h2_km: Height of the second station (km), with 0 <= h1_km < h2_km.
// phi1_deg: The local apparent elevation angle at height h1_km, in degrees, with
//           phi1_deg >= 0 deg. 0 deg=horizon, +90 deg=zenith.
// atm: (Optional) A reference atmosphere from ITU-R P.835-6.
//      Default value is MEAN_ANNUAL_GLOBAL.
// rho0_gm3: (Optional) Ground-level water vapour density (g/m3). Only applies when atm
//           is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
// Returns: The slant path gaseous attenuation, Agas (dB).
double ITURP_676_13::NonNegElevAnglSlantPathGaseousAtt(double f_GHz, double h1_km, double h2_km, 
                                                       double phi1_deg, Atm atm, double rho0_gm3)
{
	constexpr double PI = 3.14159265358979323846;
	constexpr double Re = 6371.0;

	double Agas = 0.0;
	double r_1 = 0.0;
	double n_1 = 0.0;
	double beta_1_deg = 90.0 - phi1_deg;
	double sin_beta_1 = std::sin(beta_1_deg * (PI / 180.0));

	double h_lower = h1_km;
	double h_upper = h2_km;
	std::pair<int, int> indices = LayerIndices(h_lower, h_upper);
	int i_lower = indices.first;
	int i_upper = indices.second;

	for (int i = i_lower; i < i_upper; ++i)
	{
		double h_i_bot = LayerBottomHeight(i, i_lower, i_upper, h_lower, h_upper);
		double delta_i = LayerThickness(i, i_lower, i_upper, h_lower, h_upper);
		double h_i_mid = h_i_bot + (delta_i / 2.0);
		double n_i = RefractiveIndex(h_i_mid, atm, rho0_gm3);
		double r_i = Re + h_i_bot;

		if (i == i_lower)
		{
			r_1 = r_i;
			n_1 = n_i;
		}

		double beta_i_rad = std::asin(((n_1 * r_1) / (n_i * r_i)) * sin_beta_1);
		double cos_beta_i = std::cos(beta_i_rad);
		double a_i = (-r_i * cos_beta_i) + std::sqrt((r_i * r_i * cos_beta_i * cos_beta_i) + 
													 (2.0 * r_i * delta_i) + (delta_i * delta_i));

		double T = ITURP_835_6::Temperature(h_i_mid, atm);
		double P = ITURP_835_6::Pressure(h_i_mid, atm);
		double rho = ITURP_835_6::WaterVapourDensity(h_i_mid, atm, rho0_gm3);
		double e = rho * T / 216.7; // water vapour pressure, in hPa
		double Pdry = P - e; // eq. (5) of P.453-14

		// examples from CG-3M3J-13-ValEx-Rev8.3.0.xlsx use dry pressure
		double y_i = GaseousAttenuation(f_GHz, Pdry, T, rho);
		Agas += a_i * y_i;
	}

	return Agas;
}

// ITU-R P.676-13, Annex 1, Section 2.2.2 (Negative apparent elevation angles).
// 
// Calculates the Earth-space slant path gaseous attenuation for an ascending path between a
// location on or near the surface of the Earth and a location above the surface of the Earth or
// in space.
// 
// f_GHz: Frequency in GHz, with 1 <= f_GHz <= 1000.
// h1_km: Height of the first station (km), with 0 <= h1_km < h2_km.
// h2_km: Height of the second station (km), with 0 <= h1_km < h2_km.
// phi1_deg: The local apparent elevation angle at height h1_km, in degrees, with
//           phi1_deg < 0 deg. 0 deg=horizon, -90 deg=nadir.
// atm: (Optional) A reference atmosphere from ITU-R P.835-6.
//      Default value is MEAN_ANNUAL_GLOBAL.
// rho0_gm3: (Optional) Ground-level water vapour density (g/m3). Only applies when atm
//           is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
// Returns: The slant path gaseous attenuation, Agas (dB).
double ITURP_676_13::NegElevAnglSlantPathGaseousAtt(double f_GHz, double h1_km, double h2_km, 
                                                    double phi1_deg, Atm atm, double rho0_gm3)
{
	constexpr double PI = 3.14159265358979323846;
	constexpr double Re = 6371.0;

	double beta_1_deg = 90.0 - phi1_deg;
	double sin_beta_1 = std::sin(beta_1_deg * (PI / 180.0));
	double n_h1 = RefractiveIndex(h1_km, atm, rho0_gm3);

	double hG_low = 0.0;
	double hG_high = h2_km;
	double hG = ((hG_high - hG_low) / 2.0) + hG_low;

	for (int iter = 1; iter < 24; ++iter)
	{
		double n_hG = RefractiveIndex(hG, atm, rho0_gm3);
		double gazing_test = (n_hG * (Re + hG)) - (n_h1 * (Re + h1_km) * sin_beta_1);
		if (gazing_test > 0.0)
			hG_high = hG;
		else
			hG_low = hG;
		hG = ((hG_high - hG_low) / 2.0) + hG_low;
	}

	double Agas1 = NonNegElevAnglSlantPathGaseousAtt(f_GHz, hG, h1_km, 0.0, atm, rho0_gm3);
	double Agas2 = NonNegElevAnglSlantPathGaseousAtt(f_GHz, hG, h2_km, 0.0, atm, rho0_gm3);

	return Agas1 + Agas2;
}

double ITURP_676_13::SlantPathGaseousAttenuation(double f_GHz, double h1_km, double h2_km, 
                                                 double phi1_deg, Atm atm, double rho0_gm3)
{
	if (phi1_deg >= 0.0)
		return NonNegElevAnglSlantPathGaseousAtt(f_GHz, h1_km, h2_km, phi1_deg, atm, rho0_gm3);
	else
		return NegElevAnglSlantPathGaseousAtt(f_GHz, h1_km, h2_km, phi1_deg, atm, rho0_gm3);
}

double ITURP_676_13::SpaceBasedStationApparentElevAngle(double he_km, double hs_km, double phie_deg, 
                                                        Atm atm, double rho0_gm3)
{
	constexpr double PI = 3.14159265358979323846;
	constexpr double Re = 6371.0;

	double phie_rad = phie_deg * (PI / 180.0);
	double rs = Re + hs_km;
	double ns = RefractiveIndex(hs_km, atm, rho0_gm3);
	double re = Re + he_km;
	double ne = RefractiveIndex(he_km, atm, rho0_gm3);
	double phis_rad = -std::acos(((re * ne) / (rs * ns)) * std::cos(phie_rad));
	double phis_deg = phis_rad * (180.0 / PI);

	return phis_deg;
}

double ITURP_676_13::EarthBasedStationApparentElevAngle(double he_km, double hs_km, double phis_deg, 
                                                        Atm atm, double rho0_gm3)
{
	constexpr double PI = 3.14159265358979323846;
	constexpr double Re = 6371.0;

	double phis_rad = phis_deg * (PI / 180.0);
	double rs = Re + hs_km;
	double ns = RefractiveIndex(hs_km, atm, rho0_gm3);
	double re = Re + he_km;
	double ne = RefractiveIndex(he_km, atm, rho0_gm3);
	double phie_rad = std::acos(((rs * ns) / (re * ne)) * std::cos(phis_rad));
	double phie_deg = phie_rad * (180.0 / PI);

	return phie_deg;
}

// ITU-R P.676-13, Annex 1, Section 3.
// 
// N'Oxygen.
// 
// f_GHz: Frequency (GHz), with 1 <= f_GHz <= 1000.
// p_hPa: Atmospheric pressure (hPa).
// T_K: Temperature (K).
// rho_gm3: Water vapour density (g/m3).
// Returns: Real part of the complex refractivity attributable to oxygen.
double ITURP_676_13::NpOxygen(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	double f = f_GHz;
	double P = p_hPa;
	double theta = 300.0 / T_K;
	double e = rho_gm3 * T_K / 216.7;
	double NpO = 0.0;
	double prod1 = 1.0E-7 * P * theta * theta * theta;
	double prod2 = 1.1 * e * theta;
	double prod3 = 1.0E-4 * (P + e) * std::pow(theta, 0.8);

	for (int i = 0; i < s_T1_ROW_COUNT; ++i)
	{
		double fi = s_TABLE_1[i][0];
		double a1 = s_TABLE_1[i][1];
		double a2 = s_TABLE_1[i][2];
		double a3 = s_TABLE_1[i][3];
		double a4 = s_TABLE_1[i][4];
		double a5 = s_TABLE_1[i][5];
		double a6 = s_TABLE_1[i][6];

		double Si = a1 * prod1 * std::exp(a2 * (1.0 - theta)); // eq. (3) for oxygen
		double df = a3 * 1.0E-4 * ((P * std::pow(theta, 0.8 - a4)) + prod2); // eq. (6a) for oxygen
		df = std::sqrt((df * df) + 2.25E-6); // eq. (6b) for oxygen
		double delta = (a5 + (a6 * theta)) * prod3; // eq. (7) for oxygen

		// eq. (25c)
		double Fpi = (f / fi) * ((((fi - f) + (delta * df)) / (((fi - f) * (fi - f)) + (df * df))) -
								(((fi + f) + (delta * df)) / (((fi + f) * (fi + f)) + (df * df))));
		NpO += Si * Fpi; // eq. (25a)
	}

	double d = 5.6E-4 * (P + e) * std::pow(theta, 0.8); // eq. (9)
	double NpD = (-6.14E-5 * P * theta * theta * f * f) / ((f * f) + (d * d)); // eq. (25d)
	NpO += NpD; // eq. (25a)

	return NpO;
}

// ITU-R P.676-13, Annex 1, Section 3.
// 
// N'Water Vapour.
// 
// f_GHz: Frequency (GHz), with 1 <= f_GHz <= 1000.
// p_hPa: Atmospheric pressure (hPa).
// T_K: Temperature (K).
// rho_gm3: Water vapour density (g/m3).
// Returns: Real part of the complex refractivity attributable to water vapour.
double ITURP_676_13::NpWaterVapour(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	double f = f_GHz;
	double theta = 300.0 / T_K;
	double e = rho_gm3 * T_K / 216.7;
	double NpWV = 0.0;
	double prod1 = 1.0E-1 * e * std::pow(theta, 3.5);

	for (int i = 0; i < s_T2_ROW_COUNT; ++i)
	{
		double fi = s_TABLE_2[i][0];
		double b1 = s_TABLE_2[i][1];
		double b2 = s_TABLE_2[i][2];
		double b3 = s_TABLE_2[i][3];
		double b4 = s_TABLE_2[i][4];
		double b5 = s_TABLE_2[i][5];
		double b6 = s_TABLE_2[i][6];

		double Si = b1 * prod1 * std::exp(b2 * (1.0 - theta)); // eq. (3) for water vapour
		double df = b3 * 1.0E-4 * ((p_hPa * std::pow(theta, b4)) + (b5 * e * std::pow(theta, b6))); // eq. (6a) water vapour
		df = 0.535 * df + std::sqrt((0.217 * df * df) + (2.1316E-12 * fi * fi / theta)); // eq. (6b) for water vapour

		// eq. (25c) with delta=0 (eq. (7))
		double Fpi = (f / fi) * (((fi - f) / (((fi - f) * (fi - f)) + (df * df))) - 
									((fi + f) / (((fi + f) * (fi + f)) + (df * df))));
		NpWV += Si * Fpi; // eq. (25b)
	}

	return NpWV;
}

double ITURP_676_13::PhaseDispersion(double f_GHz, double p_hPa, double T_K, double rho_gm3)
{
	double Np_oxygen = NpOxygen(f_GHz, p_hPa, T_K, rho_gm3);
	double Np_water_vapour = NpWaterVapour(f_GHz, p_hPa, T_K, rho_gm3);
	double phi = -1.2008 * f_GHz * (Np_oxygen + Np_water_vapour); // eq. (24)
	return phi;
}

// ITU-R P.676-13, Annex 1, Section 4.
double ITURP_676_13::TBFunc(double f_GHz, double Tj)
{
	double TB = 0.048 * f_GHz / (std::exp(0.048 * f_GHz / Tj) - 1.0); // eq. (26)
	return TB;
}

double ITURP_676_13::DownwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, 
                                                               double h1_km, double hk_km, 
                                                               Atm atm, double rho0_gm3)
{
	constexpr double PI = 3.14159265358979323846;
	constexpr double Re = 6371.0;

	double r_1 = 0.0;
	double n_1 = 0.0;
	double beta_1_deg = 90.0 - phi1_deg;
	double sin_beta_1 = std::sin(beta_1_deg * (PI / 180.0));

	// step 1
	double TB_dw = TBFunc(f_GHz, 2.73);

	double h_lower = h1_km;
	double h_upper = hk_km;
	std::pair<int, int> indices = LayerIndices(h_lower, h_upper);
	int i_lower = indices.first;
	int i_upper = indices.second;

	for (int i = i_lower; i < i_upper; ++i)
	{
		int j = i_upper - i;

		// step 2
		double TB_dw_last = TB_dw;

		// step 3
		double h_j_bot = LayerBottomHeight(j, i_lower, i_upper, h_lower, h_upper);
		double delta_j = LayerThickness(j, i_lower, i_upper, h_lower, h_upper);
		double h_j_mid = h_j_bot + (delta_j / 2.0);
		double Tj = ITURP_835_6::Temperature(h_j_mid, atm);
		double TB = TBFunc(f_GHz, Tj);

		// step 4
		double n_j = RefractiveIndex(h_j_mid, atm, rho0_gm3);
		double r_j = Re + h_j_bot;
		if (i == i_lower)
		{
			r_1 = r_j;
			n_1 = n_j;
		}
		double beta_j_rad = std::asin(((n_1 * r_1) / (n_j * r_j)) * sin_beta_1);
		double cos_beta_j = std::cos(beta_j_rad);
		double a_j = (-r_j * cos_beta_j) + std::sqrt((r_j * r_j * cos_beta_j * cos_beta_j) + 
														(2.0 * r_j * delta_j) + (delta_j * delta_j));

		double P = ITURP_835_6::Pressure(h_j_mid, atm);
		double rho = ITURP_835_6::WaterVapourDensity(h_j_mid, atm, rho0_gm3);
		double e = rho * Tj / 216.7; // water vapour pressure, in hPa
		double Pdry = P - e; // eq. (5) of P.453-14
		double y_j = GaseousAttenuation(f_GHz, Pdry, Tj, rho);

		// step 4
		double Lj = std::pow(10.0, (-a_j * y_j) / 10.0);

		// step 5
		TB_dw = (TB_dw_last * Lj) + ((1.0 - Lj) * TB);
	}

	return TB_dw;
}

double ITURP_676_13::UpwellingMicrowaveBrightnessTemperature(double f_GHz, double phi1_deg, 
                                                             double h1_km, double hk_km, 
                                                             Atm atm, double rho0_gm3, 
                                                             double emissivity, double TEarth_K)
{
	// Note: In ITU-R P.676-13, it seems there is an error at equations (28a) and (28c). The -1
	// value is placed outside of the denominator, contrary to eq.(26). Using eq. (28a) and (28c)
	// as is yields results that are very different than those shown in FIGURE 9. However when using
	// -1 within the denominator like in eq.(26), results match those in FIGURE 9.

	constexpr double PI = 3.14159265358979323846;
	constexpr double Re = 6371.0;

	double r_1 = 0.0;
	double n_1 = 0.0;
	double beta_1_deg = 90.0 - phi1_deg;
	double sin_beta_1 = std::sin(beta_1_deg * (PI / 180.0));

	// step 1
	double reflectivity = 1.0 - emissivity;
	double TB_dw = DownwellingMicrowaveBrightnessTemperature(f_GHz, phi1_deg, h1_km, hk_km, atm, 
																rho0_gm3);
	double TB_uw = (emissivity * TBFunc(f_GHz, TEarth_K)) + (reflectivity * TB_dw);

	double h_lower = h1_km;
	double h_upper = hk_km;
	std::pair<int, int> indices = LayerIndices(h_lower, h_upper);
	int j_lower = indices.first;
	int j_upper = indices.second;

	for (int j = j_lower; j < j_upper; ++j)
	{
		// step 2
		double TB_uw_last = TB_uw;

		// step 3
		double h_j_bot = LayerBottomHeight(j, j_lower, j_upper, h_lower, h_upper);
		double delta_j = LayerThickness(j, j_lower, j_upper, h_lower, h_upper);
		double h_j_mid = h_j_bot + (delta_j / 2.0);
		double Tj = ITURP_835_6::Temperature(h_j_mid, atm);
		double TB = TBFunc(f_GHz, Tj);

		// step 4
		double n_j = RefractiveIndex(h_j_mid, atm, rho0_gm3);
		double r_j = Re + h_j_bot;
		if (j == j_lower)
		{
			r_1 = r_j;
			n_1 = n_j;
		}
		double beta_j_rad = std::asin(((n_1 * r_1) / (n_j * r_j)) * sin_beta_1);
		double cos_beta_j = std::cos(beta_j_rad);
		double a_j = (-r_j * cos_beta_j) + std::sqrt((r_j * r_j * cos_beta_j * cos_beta_j) + 
														(2.0 * r_j * delta_j) + (delta_j * delta_j));

		double P = ITURP_835_6::Pressure(h_j_mid, atm);
		double rho = ITURP_835_6::WaterVapourDensity(h_j_mid, atm, rho0_gm3);
		double e = rho * Tj / 216.7; // water vapour pressure, in hPa
		double Pdry = P - e; // eq. (5) of P.453-14
		double y_j = GaseousAttenuation(f_GHz, Pdry, Tj, rho);

		// step 4
		double Lj = std::pow(10.0, (-a_j * y_j) / 10.0);

		// step 5
		TB_uw = (TB_uw_last * Lj) + ((1.0 - Lj) * TB);
	}

	return TB_uw;
}

// ITU-R P.676-13, Annex 2.
std::tuple<double, double, double, double> ITURP_676_13::Part1Coeffs(double f_GHz)
{
	constexpr double min_freq = 1.0;
	constexpr double freq_interval = 0.5;
	constexpr std::size_t row_size = 5;
	constexpr std::size_t num_rows = 700;

	double raw_row = std::trunc((f_GHz - min_freq) / freq_interval);
	if (f_GHz >= 118.75) // there is an extra row at 118.75 GHz
	{
		raw_row += 1.0;
	}

	std::size_t row = static_cast<std::size_t>(
		std::clamp(raw_row, 0.0, static_cast<double>(num_rows - 2))
	);

	std::size_t index0 = row * row_size;
	std::size_t index1 = (row + 1) * row_size;

	double f0 = s_PART_1_COEFFS.GetValueFromIndex(index0 + 0);
	double a0 = s_PART_1_COEFFS.GetValueFromIndex(index0 + 1);
	double b0 = s_PART_1_COEFFS.GetValueFromIndex(index0 + 2);
	double c0 = s_PART_1_COEFFS.GetValueFromIndex(index0 + 3);
	double d0 = s_PART_1_COEFFS.GetValueFromIndex(index0 + 4);

	double f1 = s_PART_1_COEFFS.GetValueFromIndex(index1 + 0);
	double a1 = s_PART_1_COEFFS.GetValueFromIndex(index1 + 1);
	double b1 = s_PART_1_COEFFS.GetValueFromIndex(index1 + 2);
	double c1 = s_PART_1_COEFFS.GetValueFromIndex(index1 + 3);
	double d1 = s_PART_1_COEFFS.GetValueFromIndex(index1 + 4);

	double a = (a0 * (f1 - f_GHz) + a1 * (f_GHz - f0)) / (f1 - f0);
	double b = (b0 * (f1 - f_GHz) + b1 * (f_GHz - f0)) / (f1 - f0);
	double c = (c0 * (f1 - f_GHz) + c1 * (f_GHz - f0)) / (f1 - f0);
	double d = (d0 * (f1 - f_GHz) + d1 * (f_GHz - f0)) / (f1 - f0);

	return {a, b, c, d};
}

// ITU-R P.676-13, Annex 2.
std::tuple<double, double, double, double> ITURP_676_13::Part2Coeffs(double f_GHz)
{
	constexpr double min_freq = 1.0;
	constexpr double freq_interval = 0.5;
	constexpr std::size_t row_size = 5;
	constexpr std::size_t num_rows = 699;

	double raw_row = std::trunc((f_GHz - min_freq) / freq_interval);

	std::size_t row = static_cast<std::size_t>(
		std::clamp(raw_row, 0.0, static_cast<double>(num_rows - 2))
	);

	std::size_t index0 = row * row_size;
	std::size_t index1 = (row + 1) * row_size;

	double f0 = s_PART_2_COEFFS.GetValueFromIndex(index0 + 0);
	double a0 = s_PART_2_COEFFS.GetValueFromIndex(index0 + 1);
	double b0 = s_PART_2_COEFFS.GetValueFromIndex(index0 + 2);
	double c0 = s_PART_2_COEFFS.GetValueFromIndex(index0 + 3);
	double d0 = s_PART_2_COEFFS.GetValueFromIndex(index0 + 4);

	double f1 = s_PART_2_COEFFS.GetValueFromIndex(index1 + 0);
	double a1 = s_PART_2_COEFFS.GetValueFromIndex(index1 + 1);
	double b1 = s_PART_2_COEFFS.GetValueFromIndex(index1 + 2);
	double c1 = s_PART_2_COEFFS.GetValueFromIndex(index1 + 3);
	double d1 = s_PART_2_COEFFS.GetValueFromIndex(index1 + 4);

	double a = (a0 * (f1 - f_GHz) + a1 * (f_GHz - f0)) / (f1 - f0);
	double b = (b0 * (f1 - f_GHz) + b1 * (f_GHz - f0)) / (f1 - f0);
	double c = (c0 * (f1 - f_GHz) + c1 * (f_GHz - f0)) / (f1 - f0);
	double d = (d0 * (f1 - f_GHz) + d1 * (f_GHz - f0)) / (f1 - f0);

	return {a, b, c, d};
}

double ITURP_676_13::SlantPathInstantOxygenGaseousAtt(double f_GHz, double theta_deg, double ps_hPa, 
                                                      double Ts_K, double rhows_gm3)
{
	constexpr double PI = 3.14159265358979323846;

	double es = rhows_gm3 * Ts_K / 216.7;
	double ps = ps_hPa - es;
	double yo = DryAirGaseousAttenuation(f_GHz, ps, Ts_K, rhows_gm3);

	double ao, bo, co, do_coeff; // Note: 'do' is a reserved C++ keyword, so we use 'do_coeff'
	std::tie(ao, bo, co, do_coeff) = Part1Coeffs(f_GHz);

	double ho = ao + bo * Ts_K + co * ps_hPa + do_coeff * rhows_gm3;
	double Ao = yo * ho / std::sin(theta_deg * (PI / 180.0));

	return Ao;
}

// ITU-R P.676-13, Annex 2, Section 1.2.
// 
// Gets the predicted slant path statistical gaseous attenuation attributable to oxygen (dB).
// The prediction method is applicable to paths between the surface of the Earth and space for
// elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.
// 
// f_GHz: Frequency of interest (GHz), with 1 <= f_GHz <= 350.
// theta_deg: Elevation angle (degrees), with 5 <= theta_deg <= 90.
// mean_ps_hPa: Mean total (barometric) surface pressure (hPa) at the desired location.
// mean_Ts_K: Mean surface temperature (K) at the desired location.
// mean_rhows_gm3: Mean surface water vapour density (g/m3) at the desired location.
// psp_hPa: Total (barometric) surface pressure at the exceedance probability p, in
//          hPa, at the desired location.
// Tsp_K: Surface temperature at the exceedance probability p, in K, at the desired
//        location.
// rhowsp_gm3: Surface water vapour density at the exceedance probability p, in g/m3,
//             at the desired location.
// Returns: The predicted slant path statistical gaseous attenuation attributable to
//          oxygen, Ao (dB).
double ITURP_676_13::SlantPathStatisticalOxygenGaseousAttHelper(double f_GHz, double theta_deg, 
                                                                double mean_ps_hPa, double mean_Ts_K, 
                                                                double mean_rhows_gm3, double psp_hPa, 
                                                                double Tsp_K, double rhowsp_gm3)
{
	constexpr double PI = 3.14159265358979323846;

	double m_es = mean_rhows_gm3 * mean_Ts_K / 216.7;
	double m_ps = mean_ps_hPa - m_es;
	double yo = DryAirGaseousAttenuation(f_GHz, m_ps, mean_Ts_K, mean_rhows_gm3);

	double ao, bo, co, do_coeff;
	std::tie(ao, bo, co, do_coeff) = Part1Coeffs(f_GHz);

	double ho = ao + bo * Tsp_K + co * psp_hPa + do_coeff * rhowsp_gm3;
	double Ao = yo * ho / std::sin(theta_deg * (PI / 180.0));

	return Ao;
}

double ITURP_676_13::SlantPathStatisticalOxygenGaseousAtt(double f_GHz, double theta_deg, 
                                                          double p_percent, double lat, double lon, 
                                                          int month, double h_mamsl)
{
	if (std::isnan(h_mamsl))
		h_mamsl = ITURP_1511_3::TopographicHeight(lat, lon);

	double psp_hPa = ITURP_2145_0::SurfaceTotalPressure(p_percent, lat, lon, month, h_mamsl);
	double Tsp_K = ITURP_2145_0::SurfaceTemperature(p_percent, lat, lon, month, h_mamsl);
	double rhowsp_gm3 = ITURP_2145_0::SurfaceWaterVapourDensity(p_percent, lat, lon, month, h_mamsl);
	double mean_ps_hPa = ITURP_2145_0::MeanSurfaceTotalPressure(lat, lon, month, h_mamsl);
	double mean_Ts_K = ITURP_2145_0::MeanSurfaceTemperature(lat, lon, month, h_mamsl);
	double mean_rhows_gm3 = ITURP_2145_0::MeanSurfaceWaterVapourDensity(lat, lon, month, h_mamsl);

	double Ao = SlantPathStatisticalOxygenGaseousAttHelper(f_GHz, theta_deg, mean_ps_hPa, mean_Ts_K, 
														   mean_rhows_gm3, psp_hPa, Tsp_K, rhowsp_gm3);
	return Ao;
}

double ITURP_676_13::SlantPathInstantWaterVapourGaseousAtt1(double f_GHz, double theta_deg, 
                                                            double ps_hPa, double Ts_K, 
                                                            double rhows_gm3)
{
	constexpr double PI = 3.14159265358979323846;

	double es = rhows_gm3 * Ts_K / 216.7;
	double ps = ps_hPa - es;
	double yw = WaterVapourGaseousAttenuation(f_GHz, ps, Ts_K, rhows_gm3);

	double hw = 5.6585E-5 * f_GHz + 1.8348;
	hw += 2.6846 / (((f_GHz - 22.235080) * (f_GHz - 22.235080)) + 2.7649);
	hw += 5.8905 / (((f_GHz - 183.310087) * (f_GHz - 183.310087)) + 4.9219);
	hw += 2.9810 / (((f_GHz - 325.152888) * (f_GHz - 325.152888)) + 3.0748);

	double Aw = yw * hw / std::sin(theta_deg * (PI / 180.0));
	return Aw;
}

double ITURP_676_13::SlantPathInstantWaterVapourGaseousAtt2(double f_GHz, double theta_deg, 
                                                            double ps_hPa, double Ts_K, 
                                                            double rhows_gm3, double Vs_kgm2)
{
	constexpr double PI = 3.14159265358979323846;

	double aV, bV, cV, dV;
	std::tie(aV, bV, cV, dV) = Part2Coeffs(f_GHz);

	double KV = aV + bV * rhows_gm3 + cV * Ts_K + dV * ps_hPa;
	double Aw = KV * Vs_kgm2 / std::sin(theta_deg * (PI / 180.0));

	return Aw;
}

// ITU-R P.676-13, Annex 2, Section 2.3.
// 
// Gets the predicted slant path statistical gaseous attenuation attributable to water vapour (dB).
// The prediction method is applicable to paths between the surface of the Earth and space for
// elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.
// 
// f_GHz: Frequency of interest (GHz), with 1 <= f_GHz <= 350.
// theta_deg: Elevation angle (deg), with 5 <= theta_deg <= 90.
// mean_ps_hPa: Mean total (barometric) surface pressure (hPa) at the desired location.
// mean_Ts_K: Mean surface temperature (K) at the desired location.
// mean_rhows_gm3: Mean surface water vapour density (g/m3) at the desired location.
// Vsp_kgm2: Integrated water vapour content at the exceedance probability p, in kg/m2
//           or mm, from the surface of the Earth at the desired location.
// Returns: The predicted slant path statistical gaseous attenuation attributable to water
//          vapour, Aw (dB).
double ITURP_676_13::SlantPathStatisticalWaterVapourGaseousAttHelper(double f_GHz, double theta_deg, 
                                                                     double mean_ps_hPa, double mean_Ts_K, 
                                                                     double mean_rhows_gm3, double Vsp_kgm2)
{
	constexpr double PI = 3.14159265358979323846;

	double aV, bV, cV, dV;
	std::tie(aV, bV, cV, dV) = Part2Coeffs(f_GHz);

	double KV = aV + bV * mean_rhows_gm3 + cV * mean_Ts_K + dV * mean_ps_hPa;
	double Aw = KV * Vsp_kgm2 / std::sin(theta_deg * (PI / 180.0));

	return Aw;
}

double ITURP_676_13::SlantPathStatisticalWaterVapourGaseousAtt(double f_GHz, double theta_deg, 
                                                               double p_percent, double lat, 
                                                               double lon, int month, 
                                                               double h_mamsl)
{
	if (std::isnan(h_mamsl))
		h_mamsl = ITURP_1511_3::TopographicHeight(lat, lon);

	double Vsp_kgm2 = ITURP_2145_0::IntegratedWaterVapourContent(p_percent, lat, lon, month, h_mamsl);
	double mean_ps_hPa = ITURP_2145_0::MeanSurfaceTotalPressure(lat, lon, month, h_mamsl);
	double mean_Ts_K = ITURP_2145_0::MeanSurfaceTemperature(lat, lon, month, h_mamsl);
	double mean_rhows_gm3 = ITURP_2145_0::MeanSurfaceWaterVapourDensity(lat, lon, month, h_mamsl);

	double Aw = SlantPathStatisticalWaterVapourGaseousAttHelper(f_GHz, theta_deg, mean_ps_hPa, 
																mean_Ts_K, mean_rhows_gm3, Vsp_kgm2);
	return Aw;
}

double ITURP_676_13::SlantPathInstantGaseousAttenuation(double f_GHz, double theta_deg, 
                                                        double ps_hPa, double Ts_K, 
                                                        double rhows_gm3, double Vs_kgm2)
{
	double Ao = SlantPathInstantOxygenGaseousAtt(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3);
	double Aw;

	if (std::isnan(Vs_kgm2))
		Aw = SlantPathInstantWaterVapourGaseousAtt1(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3);
	else
		Aw = SlantPathInstantWaterVapourGaseousAtt2(f_GHz, theta_deg, ps_hPa, Ts_K, rhows_gm3, 
													Vs_kgm2);

	return Ao + Aw;
}

double ITURP_676_13::SlantPathStatisticalGaseousAttenuation(double f_GHz, double theta_deg, 
                                                            double p_percent, double lat, 
                                                            double lon, int month, double h_mamsl)
{
	// Resolve h_mamsl once if AUTO so ITURP_2145_0 doesn't query ITURP_1511_3 seven times
	if (std::isnan(h_mamsl))
		h_mamsl = ITURP_1511_3::TopographicHeight(lat, lon);

	// Fetch the shared mean surface parameters once
	double mean_ps_hPa = ITURP_2145_0::MeanSurfaceTotalPressure(lat, lon, month, h_mamsl);
	double mean_Ts_K = ITURP_2145_0::MeanSurfaceTemperature(lat, lon, month, h_mamsl);
	double mean_rhows_gm3 = ITURP_2145_0::MeanSurfaceWaterVapourDensity(lat, lon, month, h_mamsl);

	// Fetch the exceedance probability parameters for oxygen
	double psp_hPa = ITURP_2145_0::SurfaceTotalPressure(p_percent, lat, lon, month, h_mamsl);
	double Tsp_K = ITURP_2145_0::SurfaceTemperature(p_percent, lat, lon, month, h_mamsl);
	double rhowsp_gm3 = ITURP_2145_0::SurfaceWaterVapourDensity(p_percent, lat, lon, month, h_mamsl);

	// Fetch the exceedance probability parameter for water vapour
	double Vsp_kgm2 = ITURP_2145_0::IntegratedWaterVapourContent(p_percent, lat, lon, month, h_mamsl);

	double Ao = SlantPathStatisticalOxygenGaseousAttHelper(f_GHz, theta_deg, mean_ps_hPa, 
															mean_Ts_K, mean_rhows_gm3, psp_hPa, 
															Tsp_K, rhowsp_gm3);
	double Aw = SlantPathStatisticalWaterVapourGaseousAttHelper(f_GHz, theta_deg, mean_ps_hPa, 
																mean_Ts_K, mean_rhows_gm3, Vsp_kgm2);

	return Ao + Aw;
}

// ITU-R P.676-13, Annex 2, Section 2.4.
// 
// Gets the Weibull approximation to the predicted slant path statistical gaseous attenuation
// attributable to water vapour (dB).
// 
// f_GHz: Frequency of interest (GHz), with 1 <= f_GHz <= 350.
// theta_deg: Elevation angle (degrees), with 5 <= theta_deg <= 90.
// p_percent: Exceedance probability (CCDF) of interest, in %.
// mean_ps_hPa: Mean total (barometric) surface pressure (hPa) at the desired location.
// mean_Ts_K: Mean surface temperature (K) at the desired location.
// mean_rhows_gm3: Mean surface water vapour density (g/m3) at the desired location.
// lambda_VS: Surface Weibull water vapour scale parameter at the desired location.
// k_VS: Surface Weibull water vapour shape parameter at the desired location.
// Returns: The Weibull approximation to the predicted slant path statistical gaseous
//          attenuation attributable to water vapour, Aw (dB).
double ITURP_676_13::WeibullApproximationHelper(double f_GHz, double theta_deg, double p_percent, 
                                                double mean_ps_hPa, double mean_Ts_K, 
                                                double mean_rhows_gm3, double lambda_VS, double k_VS)
{
	constexpr double PI = 3.14159265358979323846;

	double aV, bV, cV, dV;
	std::tie(aV, bV, cV, dV) = Part2Coeffs(f_GHz);

	double KV = aV + bV * mean_rhows_gm3 + cV * mean_Ts_K + dV * mean_ps_hPa;
	double Aw = lambda_VS * KV * std::pow(-std::log(p_percent / 100.0), 1.0 / k_VS) / 
				std::sin(theta_deg * (PI / 180.0));

	return Aw;
}

double ITURP_676_13::WeibullApproximation(double f_GHz, double theta_deg, double p_percent, 
                                          double lat, double lon, double h_mamsl)
{
	if (std::isnan(h_mamsl))
		h_mamsl = ITURP_1511_3::TopographicHeight(lat, lon);

	double mean_ps_hPa = ITURP_2145_0::MeanSurfaceTotalPressure(lat, lon, -1, h_mamsl);
	double mean_Ts_K = ITURP_2145_0::MeanSurfaceTemperature(lat, lon, -1, h_mamsl);
	double mean_rhows_gm3 = ITURP_2145_0::MeanSurfaceWaterVapourDensity(lat, lon, -1, h_mamsl);
	double k_VS = ITURP_2145_0::WeibullShapeParameter(lat, lon, h_mamsl);
	double lambda_VS = ITURP_2145_0::WeibullScaleParameter(lat, lon, h_mamsl);

	double Aw = WeibullApproximationHelper(f_GHz, theta_deg, p_percent, mean_ps_hPa, mean_Ts_K, 
											mean_rhows_gm3, lambda_VS, k_VS);
	return Aw;
}

const double ITURP_676_13::s_TABLE_1[ITURP_676_13::s_T1_ROW_COUNT][ITURP_676_13::s_T1_COL_COUNT]={
	{50.474214,0.975,9.651,6.690,0.0,2.566,6.850},
	{50.987745,2.529,8.653,7.170,0.0,2.246,6.800},
	{51.503360,6.193,7.709,7.640,0.0,1.947,6.729},
	{52.021429,14.320,6.819,8.110,0.0,1.667,6.640},
	{52.542418,31.240,5.983,8.580,0.0,1.388,6.526},
	{53.066934,64.290,5.201,9.060,0.0,1.349,6.206},
	{53.595775,124.600,4.474,9.550,0.0,2.227,5.085},
	{54.130025,227.300,3.800,9.960,0.0,3.170,3.750},
	{54.671180,389.700,3.182,10.370,0.0,3.558,2.654},
	{55.221384,627.100,2.618,10.890,0.0,2.560,2.952},
	{55.783815,945.300,2.109,11.340,0.0,-1.172,6.135},
	{56.264774,543.400,0.014,17.030,0.0,3.525,-0.978},
	{56.363399,1331.800,1.654,11.890,0.0,-2.378,6.547},
	{56.968211,1746.600,1.255,12.230,0.0,-3.545,6.451},
	{57.612486,2120.100,0.910,12.620,0.0,-5.416,6.056},
	{58.323877,2363.700,0.621,12.950,0.0,-1.932,0.436},
	{58.446588,1442.100,0.083,14.910,0.0,6.768,-1.273},
	{59.164204,2379.900,0.387,13.530,0.0,-6.561,2.309},
	{59.590983,2090.700,0.207,14.080,0.0,6.957,-0.776},
	{60.306056,2103.400,0.207,14.150,0.0,-6.395,0.699},
	{60.434778,2438.000,0.386,13.390,0.0,6.342,-2.825},
	{61.150562,2479.500,0.621,12.920,0.0,1.014,-0.584},
	{61.800158,2275.900,0.910,12.630,0.0,5.014,-6.619},
	{62.411220,1915.400,1.255,12.170,0.0,3.029,-6.759},
	{62.486253,1503.000,0.083,15.130,0.0,-4.499,0.844},
	{62.997984,1490.200,1.654,11.740,0.0,1.856,-6.675},
	{63.568526,1078.000,2.108,11.340,0.0,0.658,-6.139},
	{64.127775,728.700,2.617,10.880,0.0,-3.036,-2.895},
	{64.678910,461.300,3.181,10.380,0.0,-3.968,-2.590},
	{65.224078,274.000,3.800,9.960,0.0,-3.528,-3.680},
	{65.764779,153.000,4.473,9.550,0.0,-2.548,-5.002},
	{66.302096,80.400,5.200,9.060,0.0,-1.660,-6.091},
	{66.836834,39.800,5.982,8.580,0.0,-1.680,-6.393},
	{67.369601,18.560,6.818,8.110,0.0,-1.956,-6.475},
	{67.900868,8.172,7.708,7.640,0.0,-2.216,-6.545},
	{68.431006,3.397,8.652,7.170,0.0,-2.492,-6.600},
	{68.960312,1.334,9.650,6.690,0.0,-2.773,-6.650},
	{118.750334,940.300,0.010,16.640,0.0,-0.439,0.079},
	{368.498246,67.400,0.048,16.400,0.0,0.000,0.000},
	{424.763020,637.700,0.044,16.400,0.0,0.000,0.000},
	{487.249273,237.400,0.049,16.000,0.0,0.000,0.000},
	{715.392902,98.100,0.145,16.000,0.0,0.000,0.000},
	{773.839490,572.300,0.141,16.200,0.0,0.000,0.000},
	{834.145546,183.100,0.145,14.700,0.0,0.000,0.000}
};

const double ITURP_676_13::s_TABLE_2[ITURP_676_13::s_T2_ROW_COUNT][ITURP_676_13::s_T2_COL_COUNT]={
	{22.235080,.1079,2.144,26.38,.76,5.087,1.00},
	{67.803960,.0011,8.732,28.58,.69,4.930,.82},
	{119.995940,.0007,8.353,29.48,.70,4.780,.79},
	{183.310087,2.273,.668,29.06,.77,5.022,.85},
	{321.225630,.0470,6.179,24.04,.67,4.398,.54},
	{325.152888,1.514,1.541,28.23,.64,4.893,.74},
	{336.227764,.0010,9.825,26.93,.69,4.740,.61},
	{380.197353,11.67,1.048,28.11,.54,5.063,.89},
	{390.134508,.0045,7.347,21.52,.63,4.810,.55},
	{437.346667,.0632,5.048,18.45,.60,4.230,.48},
	{439.150807,.9098,3.595,20.07,.63,4.483,.52},
	{443.018343,.1920,5.048,15.55,.60,5.083,.50},
	{448.001085,10.41,1.405,25.64,.66,5.028,.67},
	{470.888999,.3254,3.597,21.34,.66,4.506,.65},
	{474.689092,1.260,2.379,23.20,.65,4.804,.64},
	{488.490108,.2529,2.852,25.86,.69,5.201,.72},
	{503.568532,.0372,6.731,16.12,.61,3.980,.43},
	{504.482692,.0124,6.731,16.12,.61,4.010,.45},
	{547.676440,.9785,.158,26.00,.70,4.500,1.00},
	{552.020960,.1840,.158,26.00,.70,4.500,1.00},
	{556.935985,497.0,.159,30.86,.69,4.552,1.00},
	{620.700807,5.015,2.391,24.38,.71,4.856,.68},
	{645.766085,.0067,8.633,18.00,.60,4.000,.50},
	{658.005280,.2732,7.816,32.10,.69,4.140,1.00},
	{752.033113,243.4,.396,30.86,.68,4.352,.84},
	{841.051732,.0134,8.177,15.90,.33,5.760,.45},
	{859.965698,.1325,8.055,30.60,.68,4.090,.84},
	{899.303175,.0547,7.914,29.85,.68,4.530,.90},
	{902.611085,.0386,8.429,28.65,.70,5.100,.95},
	{906.205957,.1836,5.110,24.08,.70,4.700,.53},
	{916.171582,8.400,1.441,26.73,.70,5.150,.78},
	{923.112692,.0079,10.293,29.00,.70,5.000,.80},
	{970.315022,9.009,1.919,25.50,.64,4.940,.67},
	{987.926764,134.6,.257,29.85,.68,4.550,.90},
	{1780.000000,17506.,.952,196.3,2.00,24.15,5.00}
};

// NOTE: coefficients files are not digital maps (not location dependent), but we will use the
// DigitalMap class to tread-safely access their content. Only the number of rows and number of
// columns matter here, other lat/lon related parameters are irrelevant (won't be used).
const DigitalMap ITURP_676_13::s_PART_1_COEFFS("p676_13/R11010000020001TXTM.txt",
	-90.0, +1.0, 700, -180.0, +1.0, 5, InterpolationType::Bilinear);

const DigitalMap ITURP_676_13::s_PART_2_COEFFS("p676_13/R11010000020002TXTM.txt",
	-90.0, +1.0, 699, -180.0, +1.0, 5, InterpolationType::Bilinear);
