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
#include <stdexcept>


double ITURP_2108_1::HeightGainTerminalCorrection(double f_GHz, double h_m, ITURP_2108_1::ClutterCategory clut,
                                                  double R_m/*=AUTO*/, double ws_m/*=27.0*/)
{
	double Ah = 0.0;

	if( std::isnan(R_m) )
	{
		if (clut==ClutterCategory::WATER_SEA || clut==ClutterCategory::OPEN_RURAL || clut==ClutterCategory::SUBURBAN)
			R_m = 10.0;
		else if (clut==ClutterCategory::URBAN_TREES_FOREST)
			R_m = 15.0;
		else if (clut==ClutterCategory::DENSE_URBAN)
			R_m = 20.0;
		else
			throw std::invalid_argument("Unrecognized value for clut.");
	}

	if( h_m < R_m)
	{
		if (clut==ClutterCategory::SUBURBAN || clut==ClutterCategory::URBAN_TREES_FOREST || clut==ClutterCategory::DENSE_URBAN)
		{
			constexpr double PI_ON_180 = 0.017453292519943295769;
            const double Knu = 0.342*std::sqrt(f_GHz);
            const double hDif = R_m - h_m;
            const double thetaClut_deg = PI_ON_180*(std::atan(hDif/ws_m));
            const double v = Knu*std::sqrt(hDif*thetaClut_deg);
			double Jv = 0.0;
			if( v > -0.78 )
                Jv = 6.9 + 20.0*std::log10(std::sqrt((v-0.1)*(v-0.1)+1.0)+v-0.1);
            Ah = Jv - 6.03;
		}
		else if (clut==ClutterCategory::WATER_SEA || clut==ClutterCategory::OPEN_RURAL)
		{
            const double Kh2 = 21.8 + 6.2*std::log10(f_GHz);
            Ah = -Kh2*std::log10(h_m/R_m);
		}
		else
			throw std::invalid_argument("Unrecognized value for clut.");
	}

	return Ah;
}

double ITURP_2108_1::TerrestrialPathClutterLoss(double f_GHz, double d_km, double p_percent)
{
	const double log10_f = std::log10(f_GHz);
	double Ls = 32.98 + 23.9*std::log10(d_km) + 3.0*log10_f;
	const double Ll = -2.0*std::log10(std::pow(10.0, -5.0*log10_f-12.5)+std::pow(10.0, -16.5));
	const double pow_Ll = std::pow(10.0, -0.2*Ll);
	double pow_Ls = std::pow(10.0, -0.2*Ls);
	double sigma_cb = std::sqrt((16.0*pow_Ll+36.0*pow_Ls) / (pow_Ll+pow_Ls));
	const double QinvP = ITURP_1057_7::Qinv(p_percent/100.0);
	const double Lctt = -5.0*std::log10(pow_Ll+pow_Ls) - sigma_cb*QinvP;

	Ls = 32.98 + 23.9*std::log10(2.0) + 3.0*log10_f;
	pow_Ls = std::pow(10.0, -0.2*Ls);
	sigma_cb = std::sqrt((16.0*pow_Ll+36.0*pow_Ls) / (pow_Ll+pow_Ls));
	const double Lctt2km = -5.0*std::log10(pow_Ll+pow_Ls) - sigma_cb*QinvP;

	return std::min(Lctt, Lctt2km);
}

double ITURP_2108_1::EarthSpaceClutterLoss(double f_GHz, double theta_deg, double p_percent)
{
	constexpr double A1 = 0.05;
	constexpr double PI = 3.14159265358979323846;
	const double K1 = 93.0*std::pow(f_GHz, 0.175);
	const double a = -K1*(std::log(1.0-(p_percent/100.0)));
	const double b = 1.0/std::tan((A1*(1.0-(theta_deg/90.0)))+(PI*theta_deg/180.0));
	const double QinvP = ITURP_1057_7::Qinv(p_percent/100.0);
	const double Lces = std::pow(a*b, 0.5*(90.0-theta_deg)/90.0)-1.0-(0.6*QinvP);
	return Lces;
}
