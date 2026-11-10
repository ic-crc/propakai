/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_835_6.h"
#include <cmath>
#include <algorithm>
#include <stdexcept>


double ITURP_835_6::Temperature(double h_km, ReferenceAtmosphere atm)
{
	if (h_km < 0.0 || h_km > 100.0)
		throw std::invalid_argument("h_km is out of range.");

	double T;
	if (atm == ReferenceAtmosphere::MEAN_ANNUAL_GLOBAL)
		T = MagraTemperature(h_km);
	else if (atm == ReferenceAtmosphere::LOW_LATITUDE)
		T = LowLatTemperature(h_km);
	else if (atm == ReferenceAtmosphere::MID_LATITUDE_SUMMER)
		T = SummerMidLatTemperature(h_km);
	else if (atm == ReferenceAtmosphere::MID_LATITUDE_WINTER)
		T = WinterMidLatTemperature(h_km);
	else if (atm == ReferenceAtmosphere::HIGH_LATITUDE_SUMMER)
		T = SummerHighLatTemperature(h_km);
	else if (atm == ReferenceAtmosphere::HIGH_LATITUDE_WINTER)
		T = WinterHighLatTemperature(h_km);
	else
		throw std::invalid_argument("Invalid value for atm.");

	return T;
}

double ITURP_835_6::Pressure(double h_km, ReferenceAtmosphere atm)
{
	if (h_km < 0.0 || h_km > 100.0)
		throw std::invalid_argument("h_km is out of range.");

	double P;
	if (atm == ReferenceAtmosphere::MEAN_ANNUAL_GLOBAL)
		P = MagraPressure(h_km);
	else if (atm == ReferenceAtmosphere::LOW_LATITUDE)
		P = LowLatPressure(h_km);
	else if (atm == ReferenceAtmosphere::MID_LATITUDE_SUMMER)
		P = SummerMidLatPressure(h_km);
	else if (atm == ReferenceAtmosphere::MID_LATITUDE_WINTER)
		P = WinterMidLatPressure(h_km);
	else if (atm == ReferenceAtmosphere::HIGH_LATITUDE_SUMMER)
		P = SummerHighLatPressure(h_km);
	else if (atm == ReferenceAtmosphere::HIGH_LATITUDE_WINTER)
		P = WinterHighLatPressure(h_km);
	else
		throw std::invalid_argument("Invalid value for atm.");

	return P;
}

double ITURP_835_6::WaterVapourDensity(double h_km, ReferenceAtmosphere atm, double rho0_gm3, double h0_km)
{
	if (h_km < 0.0 || h_km > 100.0)
		throw std::invalid_argument("h_km is out of range.");

	double rho = 0.0;
	if (atm == ReferenceAtmosphere::MEAN_ANNUAL_GLOBAL)
	{
		rho = rho0_gm3*std::exp(-h_km/h0_km);

		// See Section 1.2 of Annex 1
		double P = Pressure(h_km, atm);
		if (rho/P < 2E-6)
		{
			double T = Temperature(h_km, atm);
			rho = 2E-6*216.7*P/T;
			// make sure rho is not higher than the specified ground-level rho
			// i.e. to always return 0 if rho0_gm3 is 0
			rho = std::min(rho, rho0_gm3);
		}
	}
	else if (atm == ReferenceAtmosphere::LOW_LATITUDE)
		rho = LowLatWaterVapourDensity(h_km);
	else if (atm == ReferenceAtmosphere::MID_LATITUDE_SUMMER)
		rho = SummerMidLatWaterVapourDensity(h_km);
	else if (atm == ReferenceAtmosphere::MID_LATITUDE_WINTER)
		rho = WinterMidLatWaterVapourDensity(h_km);
	else if (atm == ReferenceAtmosphere::HIGH_LATITUDE_SUMMER)
		rho = SummerHighLatWaterVapourDensity(h_km);
	else if (atm == ReferenceAtmosphere::HIGH_LATITUDE_WINTER)
		rho = WinterHighLatWaterVapourDensity(h_km);
	else
		throw std::invalid_argument("Invalid value for atm.");

	return rho;
}

double ITURP_835_6::GeometricToGeopotentialHeight(double h_km)
{
	return (6356.766*h_km)/(6356.766 + h_km);
}

double ITURP_835_6::GeopotentialToGeometricHeight(double hp_km)
{
	return (6356.766*hp_km)/(6356.766 - hp_km);
}

double ITURP_835_6::MagraPressure(double h)
{
	if (h < 86.0)
	{
		double hp = GeometricToGeopotentialHeight(h);
		if (hp <= 11.0)
			return 1013.25*std::pow(288.15/(288.15 - 6.5*hp), -34.1632/6.5);
		else if (hp <= 20.0)
			return 226.3226*std::exp(-34.1632*(hp - 11.0)/216.65);
		else if (hp <= 32.0)
			return 54.74980*std::pow(216.65/(216.65 + (hp - 20.0)), 34.1632);
		else if (hp <= 47.0)
			return 8.680422*std::pow(228.65/(228.65 + 2.8*(hp - 32.0)), 34.1632/2.8);
		else if (hp <= 51.0)
			return 1.109106*std::exp(-34.1632*(hp - 47.0)/270.65);
		else if (hp <= 71.0)
			return 0.6694167*std::pow(270.65/(270.65 - 2.8*(hp - 51.0)), -34.1632/2.8);
		return 0.03956649*std::pow(214.65/(214.65 - 2.0*(hp - 71.0)), -34.1632/2.0);
	}
	return std::exp(95.571899 - (4.011801*h) + (6.424731E-2*h*h) - (4.789660E-4*h*h*h) +
	                (1.340543E-6*h*h*h*h));
}

double ITURP_835_6::MagraTemperature(double h)
{
	if (h < 86.0)
	{
		double hp = GeometricToGeopotentialHeight(h);
		if (hp <= 11.0)
			return 288.15 - (6.5*hp);
		else if (hp <= 20.0)
			return 216.65;
		else if (hp <= 32.0)
			return 216.65 + (hp - 20.0);
		else if (hp <= 47.0)
			return 228.65 + (2.8*(hp - 32.0));
		else if (hp <= 51.0)
			return 270.65;
		else if (hp <= 71.0)
			return 270.65 - (2.8*(hp - 51.0));
		return 214.65 - (2.0*(hp - 71.0));
	}
	if (h <= 91.0)
		return 186.8673;
	double x = (h - 91.0)/19.9429;
	return 263.1905 - 76.3232*std::sqrt(1.0 - (x*x));
}

double ITURP_835_6::LowLatTemperature(double h)
{
	if (h < 17.0)
		return 300.4222 - (6.3533*h) + (0.005886*h*h);
	else if (h < 47.0)
		return 194.0 + ((h - 17.0)*2.533);
	else if (h < 52.0)
		return 270.0;
	else if (h < 80.0)
		return 270.0 - ((h - 52.0)*3.0714);
	return 184.0;
}

double ITURP_835_6::LowLatPressure(double h)
{
	if (h <= 10.0)
		return 1012.0306 - (109.0338*h) + (3.6316*h*h);
	else if (h <= 72.0)
		return LowLatPressure(10.0)*std::exp(-0.147*(h - 10.0));
	return LowLatPressure(72.0)*std::exp(-0.165*(h - 72.0));
}

double ITURP_835_6::LowLatWaterVapourDensity(double h)
{
	if (h <= 15.0)
		return 19.6542*std::exp(-(0.2313*h) - (0.1122*h*h) + (0.01351*h*h*h) - (0.0005923*h*h*h*h));
	return 0.0;
}

double ITURP_835_6::SummerMidLatTemperature(double h)
{
	if (h < 13.0)
		return 294.9838 - (5.2159*h) - (0.07109*h*h);
	else if (h < 17.0)
		return 215.15;
	else if (h < 47.0)
		return 215.15*std::exp((h - 17.0)*0.008128);
	else if (h < 53.0)
		return 275.0;
	else if (h < 80.0)
		return 275.0 + ((1.0 - std::exp((h - 53.0)*0.06))*20.0);
	return 175.0;
}

double ITURP_835_6::SummerMidLatPressure(double h)
{
	if (h <= 10.0)
		return 1012.8186 - (111.5569*h) + (3.8646*h*h);
	else if (h <= 72.0)
		return SummerMidLatPressure(10.0)*std::exp(-0.147*(h - 10.0));
	return SummerMidLatPressure(72.0)*std::exp(-0.165*(h - 72.0));
}

double ITURP_835_6::SummerMidLatWaterVapourDensity(double h)
{
	if (h <= 15.0)
		return 14.3542*std::exp(-(0.4174*h) - (0.02290*h*h) + (0.001007*h*h*h));
	return 0.0;
}

double ITURP_835_6::WinterMidLatTemperature(double h)
{
	if (h < 10.0)
		return 272.7241 - (3.6217*h) - (0.1759*h*h);
	else if (h < 33.0)
		return 218.0;
	else if (h < 47.0)
		return 218.0 + ((h - 33.0)*3.3571);
	else if (h < 53.0)
		return 265.0;
	else if (h < 80.0)
		return 265.0 - ((h - 53.0)*2.0370);
	return 210.0;
}

double ITURP_835_6::WinterMidLatPressure(double h)
{
	if (h <= 10.0)
		return 1018.8627 - (124.2954*h) + (4.8307*h*h);
	else if (h <= 72.0)
		return WinterMidLatPressure(10.0)*std::exp(-0.147*(h - 10.0));
	return WinterMidLatPressure(72.0)*std::exp(-0.155*(h - 72.0));
}

double ITURP_835_6::WinterMidLatWaterVapourDensity(double h)
{
	if (h <= 10.0)
		return 3.4742*std::exp(-(0.2697*h) - (0.03604*h*h) + (0.0004489*h*h*h));
	return 0.0;
}

double ITURP_835_6::SummerHighLatTemperature(double h)
{
	if (h < 10.0)
		return 286.8374 - (4.7805*h) - (0.1402*h*h);
	else if (h < 23.0)
		return 225.0;
	else if (h < 48.0)
		return 225.0*std::exp((h - 23.0)*0.008317);
	else if (h < 53.0)
		return 277.0;
	else if (h < 79.0)
		return 277.0 - ((h - 53.0)*4.0769);
	return 171.0;
}

double ITURP_835_6::SummerHighLatPressure(double h)
{
	if (h <= 10.0)
		return 1008.0278 - (113.2494*h) + (3.9408*h*h);
	else if (h <= 72.0)
		return SummerHighLatPressure(10.0)*std::exp(-0.140*(h - 10.0));
	return SummerHighLatPressure(72.0)*std::exp(-0.165*(h - 72.0));
}

double ITURP_835_6::SummerHighLatWaterVapourDensity(double h)
{
	if (h <= 15.0)
		return 8.988*std::exp(-(0.3614*h) - (0.005402*h*h) - (0.001955*h*h*h));
	return 0.0;
}

double ITURP_835_6::WinterHighLatTemperature(double h)
{
	if (h < 8.5)
		return 257.4345 + (2.3474*h) - (1.5479*h*h) + (0.08473*h*h*h);
	else if (h < 30.0)
		return 217.5;
	else if (h < 50.0)
		return 217.5 + ((h - 30.0)*2.125);
	else if (h < 54.0)
		return 260.0;
	return 260.0 - ((h - 54.0)*1.667);
}

double ITURP_835_6::WinterHighLatPressure(double h)
{
	if (h <= 10.0)
		return 1010.8828 - (122.2411*h) + (4.554*h*h);
	else if (h <= 72.0)
		return WinterHighLatPressure(10.0)*std::exp(-0.147*(h - 10.0));
	return WinterHighLatPressure(72.0)*std::exp(-0.150*(h - 72.0));
}

double ITURP_835_6::WinterHighLatWaterVapourDensity(double h)
{
	if (h <= 10.0)
		return 1.2319*std::exp((0.07481*h) - (0.0981*h*h) + (0.00281*h*h*h));
	return 0.0;
}
