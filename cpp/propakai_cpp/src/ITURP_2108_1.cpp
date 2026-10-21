/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_2108_1.h"
#include "ITURP_1057_7.h"
#include <cmath>
#include <algorithm>


// ITU-R P.2108-1, Annex 1, Section 3.1
// f_GHz:            frequency (GHz) [0.03, 3.0]
// h_m:              antenna height (m) [0.0, +inf.]
// clut:             clutter category
// R_m:              representative clutter height (m). Default is 0.0. If R_m <= 0, uses defaults from TABLE 3.
// ws_m:             street width (m). Default is 27.0.
// [return]:         additional loss (dB)
double ITURP_2108_1::HeightGainTerminalCorrection(double f_GHz, double h_m, ITURP_2108_1::ClutterCategory clut,
                                                  double R_m/*=0.0*/, double ws_m/*=27.0*/)
{
	double Ah = 0.0;

	if( R_m <= 0 )
	{
		if( clut == ClutterCategory::URBAN_TREES_FOREST )
			R_m = 15.0;
		else if( clut == ClutterCategory::DENSE_URBAN )
			R_m = 20.0;
		else
			R_m = 10.0;
	}

	if( h_m < R_m)
	{
		if( clut==ClutterCategory::SUBURBAN || clut==ClutterCategory::URBAN_TREES_FOREST || clut==ClutterCategory::DENSE_URBAN )
		{
			constexpr double PI_ON_180 = 0.017453292519943295769;
            const double Knu = 0.342*sqrt(f_GHz);
            const double hDif = R_m - h_m;
            const double thetaClut_deg = PI_ON_180*(atan(hDif/ws_m));
            const double v = Knu*sqrt(hDif*thetaClut_deg);
			double Jv = 0.0;
			if( v > -0.78 )
                Jv = 6.9 + 20.0*log10(sqrt((v-0.1)*(v-0.1)+1.0)+v-0.1);
            Ah = Jv - 6.03;
		}
		else
		{
            const double Kh2 = 21.8 + 6.2*log10(f_GHz);
            Ah = -Kh2*log10(h_m/R_m);
		}
	}

	return Ah;
}


// ITU-R P.2108-1, Annex 1, Section 3.2
// f_GHz:            frequency (GHz) [0.5, 67.0]
// distance_km:      distance (km) [0.25, +inf.]
// location_percent: percentage of locations (%) ]0, 100.0[
// [return]:         clutter loss (dB)
double ITURP_2108_1::TerrestrialPathClutterLoss(double f_GHz, double distance_km, double location_percent)
{
	const double f = f_GHz;
	const double d = distance_km;
	const double p = location_percent;

	const double log10_f = log10(f);
	double Ls = 32.98 + 23.9*log10(d) + 3.0*log10_f;
	const double Ll = -2.0*log10(pow(10.0, -5.0*log10_f-12.5)+pow(10.0, -16.5));
	const double pow_Ll = pow(10.0, -0.2*Ll);
	double pow_Ls = pow(10.0, -0.2*Ls);
	double sigma_cb = sqrt((16.0*pow_Ll+36.0*pow_Ls) / (pow_Ll+pow_Ls));
	const double QinvP = ITURP_1057_7::Qinv(p/100.0);
	const double Lctt = -5.0*log10(pow_Ll+pow_Ls) - sigma_cb*QinvP;

	Ls = 32.98 + 23.9*log10(2.0) + 3.0*log10_f;
	pow_Ls = pow(10.0, -0.2*Ls);
	sigma_cb = sqrt((16.0*pow_Ll+36.0*pow_Ls) / (pow_Ll+pow_Ls));
	const double Lctt2km = -5.0*log10(pow_Ll+pow_Ls) - sigma_cb*QinvP;

	return std::min(Lctt, Lctt2km);
}


// ITU-R P.2108-1, Annex 1, Section 3.3
// f_GHz:            frequency (GHz) [0.5, 67.0]
// theta_deg:        elevation angle (degrees) [0.0, 90.0]
// location_percent: percentage of locations (%) ]0, 100.0[
// [return]:         additional clutter loss (dB)
double ITURP_2108_1::EarthSpaceClutterLoss(double f_GHz, double theta_deg, double location_percent)
{
	constexpr double A1 = 0.05;
	constexpr double PI = 3.14159265358979323846;
	const double K1 = 93.0*pow(f_GHz, 0.175);
	const double a = -K1*(log(1.0-(location_percent/100.0)));
	const double b = 1.0/tan((A1*(1.0-(theta_deg/90.0)))+(PI*theta_deg/180.0));
	const double QinvP = ITURP_1057_7::Qinv(location_percent/100.0);
	const double Lces = pow(a*b, 0.5*(90.0-theta_deg)/90.0)-1.0-(0.6*QinvP);
	return Lces;
}
