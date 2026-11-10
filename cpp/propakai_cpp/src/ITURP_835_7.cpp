/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_835_7.h"
#include <cmath>
#include <stdexcept>



double ITURP_835_7::Temperature(double z_km, ReferenceAtmosphere atm, double lat)
{
	if (z_km < 0.0 || z_km > 100.0)
		throw std::invalid_argument("z_km is out of range.");

	double T;
	if (atm == ITU_R)
		T = ItuRTemperature(z_km);
	else
		T = SeasonalInterpolate(z_km, atm, lat,
		                        LowLatTemperature,
		                        SummerMidLatTemperature,
		                        WinterMidLatTemperature,
		                        SummerHighLatTemperature,
		                        WinterHighLatTemperature);
	return T;
}

double ITURP_835_7::Pressure(double z_km, ReferenceAtmosphere atm, double lat)
{
	if (z_km < 0.0 || z_km > 100.0)
		throw std::invalid_argument("z_km is out of range.");

	double P;
	if (atm == ITU_R)
		P = ItuRPressure(z_km);
	else
		P = SeasonalInterpolate(z_km, atm, lat,
		                        LowLatPressure,
		                        SummerMidLatPressure,
		                        WinterMidLatPressure,
		                        SummerHighLatPressure,
		                        WinterHighLatPressure);
	return P;
}

double ITURP_835_7::WaterVapourDensity(double z_km, ReferenceAtmosphere atm, double lat)
{
	if (z_km < 0.0 || z_km > 100.0)
		throw std::invalid_argument("z_km is out of range.");

	double rho;
	if (atm == ITU_R)
	{
		rho = 7.5*std::exp(-z_km/2.0);
		double T = Temperature(z_km);
		double e = rho*T/216.7;
		double P = Pressure(z_km);
		if (e/P < 2E-6)
			rho = 2E-6*P*216.7/T;
	}
	else
		rho = SeasonalInterpolate(z_km, atm, lat,
		                          LowLatWaterVapourDensity,
		                          SummerMidLatWaterVapourDensity,
		                          WinterMidLatWaterVapourDensity,
		                          SummerHighLatWaterVapourDensity,
		                          WinterHighLatWaterVapourDensity);
	return rho;
}

// ITU-R P.835-7, Annex 1, Section 1.1.
//
// Converts geometric height (km) to geopotential height (km).
//
// Args:
//     z_km (double): Geometric height (km).
//
// Returns:
//     H (double): Geopotential height (km).
double ITURP_835_7::GeometricToGeopotentialHeight(double z_km)
{
	return (6356.766*z_km)/(6356.766 + z_km);
}

// ITU-R P.835-7, Annex 1, Section 1.1.
//
// Converts geopotential height (km) to geometric height (km).
//
// Args:
//     h_km (double): Geopotential height (km).
//
// Returns:
//     Z (double): Geometric height (km).
double ITURP_835_7::GeopotentialToGeometricHeight(double h_km)
{
	return (6356.766*h_km)/(6356.766 - h_km);
}

// ITU-R P.835-7, Annex 1, Section 1.1.
//
// Returns temperature (K) from geometric height (km).
double ITURP_835_7::ItuRTemperature(double z_km)
{
	if (z_km < 86.0)
	{
		double H = GeometricToGeopotentialHeight(z_km);
		if (H <= 11.0)
			return 288.15 - (6.5*H);
		else if (H <= 20.0)
			return 216.65;
		else if (H <= 32.0)
			return 216.65 + (H - 20.0);
		else if (H <= 47.0)
			return 228.65 + (2.8*(H - 32.0));
		else if (H <= 51.0)
			return 270.65;
		else if (H <= 71.0)
			return 270.65 - (2.8*(H - 51.0));
		return 214.65 - (2.0*(H - 71.0));
	}
	if (z_km <= 91.0)
		return 186.8673;
	double x = (z_km - 91.0)/19.9429;
	return 263.1905 - 76.3232*std::sqrt(1.0 - (x*x));
}

// ITU-R P.835-7, Annex 1, Section 1.1.
//
// Returns pressure (hPa) from geometric height (km).
double ITURP_835_7::ItuRPressure(double z_km)
{
	double Z = z_km;
	if (Z < 86.0)
	{
		double H = GeometricToGeopotentialHeight(Z);
		if (H <= 11.0)
			return 1013.25*std::pow(288.15/(288.15 - 6.5*H), -34.1632/6.5);
		else if (H <= 20.0)
			return 226.3226*std::exp(-34.1632*(H - 11.0)/216.65);
		else if (H <= 32.0)
			return 54.74980*std::pow(216.65/(216.65 + (H - 20.0)), 34.1632);
		else if (H <= 47.0)
			return 8.680422*std::pow(228.65/(228.65 + 2.8*(H - 32.0)), 34.1632/2.8);
		else if (H <= 51.0)
			return 1.109106*std::exp(-34.1632*(H - 47.0)/270.65);
		else if (H <= 71.0)
			return 0.6694167*std::pow(270.65/(270.65 - 2.8*(H - 51.0)), -34.1632/2.8);
		return 0.03956649*std::pow(214.65/(214.65 - 2.0*(H - 71.0)), -34.1632/2.0);
	}
	return std::exp(95.571899 - (4.011801*Z) + (6.424731E-2*Z*Z) - (4.789660E-4*Z*Z*Z) +
	                (1.340543E-6*Z*Z*Z*Z));
}

// ITU-R P.835-7, Annex 2, Section 1.1.
//
// Returns the temperature (K) from geometric height (km) for low latitude (15 deg N) and all
// seasons.
double ITURP_835_7::LowLatTemperature(double z_km)
{
	if (z_km < 17.0)
		return 300.4222 - (6.3533*z_km) + (0.005886*z_km*z_km);
	else if (z_km < 47.0)
		return 194.0 + ((z_km - 17.0)*2.533);
	else if (z_km < 52.0)
		return 270.0;
	else if (z_km < 80.0)
		return 270.0 - ((z_km - 52.0)*3.0714);
	return 184.0;
}

// ITU-R P.835-7, Annex 2, Section 1.1.
//
// Returns the total (barometric) pressure (hPa) from geometric height (km) for low latitude
// (15 deg N) and all seasons.
double ITURP_835_7::LowLatPressure(double z_km)
{
	if (z_km <= 10.0)
		return 1012.0306 - (109.0338*z_km) + (3.6316*z_km*z_km);
	else if (z_km <= 72.0)
		return LowLatPressure(10.0)*std::exp(-0.147*(z_km - 10.0));
	return LowLatPressure(72.0)*std::exp(-0.165*(z_km - 72.0));
}

// ITU-R P.835-7, Annex 2, Section 1.1.
//
// Returns the water vapour density (g/m3) from geometric height (km) for low latitude
// (15 deg N) and all seasons.
double ITURP_835_7::LowLatWaterVapourDensity(double z_km)
{
	if (z_km <= 15.0)
		return 19.6542*std::exp(-(0.2313*z_km) - (0.1122*z_km*z_km) + (0.01351*z_km*z_km*z_km) -
		                        (0.0005923*z_km*z_km*z_km*z_km));
	return 0.0;
}

// ITU-R P.835-7, Annex 2, Section 1.2.1.
//
// Returns the temperature (K) from geometric height (km) for summer at mid latitude (45 deg N).
double ITURP_835_7::SummerMidLatTemperature(double z_km)
{
	if (z_km < 13.0)
		return 294.9838 - (5.2159*z_km) - (0.07109*z_km*z_km);
	else if (z_km < 17.0)
		return 215.15;
	else if (z_km < 47.0)
		return 215.15*std::exp((z_km - 17.0)*0.008128);
	else if (z_km < 53.0)
		return 275.0;
	else if (z_km < 80.0)
		return 275.0 + 111.57755*(1.0 - std::exp(0.0237*(z_km - 53.0)));
	return 175.0;
}

// ITU-R P.835-7, Annex 2, Section 1.2.1.
//
// Returns the total (barometric) pressure (hPa) from geometric height (km) for summer at mid
// latitude (45 deg N).
double ITURP_835_7::SummerMidLatPressure(double z_km)
{
	if (z_km <= 10.0)
		return 1012.8186 - (111.5569*z_km) + (3.8646*z_km*z_km);
	else if (z_km <= 72.0)
		return SummerMidLatPressure(10.0)*std::exp(-0.147*(z_km - 10.0));
	return SummerMidLatPressure(72.0)*std::exp(-0.165*(z_km - 72.0));
}

// ITU-R P.835-7, Annex 2, Section 1.2.1.
//
// Returns the water vapour density (g/m3) from geometric height (km) for summer at mid latitude
// (45 deg N).
double ITURP_835_7::SummerMidLatWaterVapourDensity(double z_km)
{
	if (z_km <= 15.0)
		return 14.3542*std::exp(-(0.4174*z_km) - (0.02290*z_km*z_km) + (0.001007*z_km*z_km*z_km));
	return 0.0;
}

// ITU-R P.835-7, Annex 2, Section 1.2.2.
//
// Returns the temperature (K) from geometric height (km) for winter at mid latitude (45 deg N).
double ITURP_835_7::WinterMidLatTemperature(double z_km)
{
	if (z_km < 10.0)
		return 272.7241 - (3.6217*z_km) - (0.1759*z_km*z_km);
	else if (z_km < 33.0)
		return 218.0;
	else if (z_km < 47.0)
		return 218.0 + ((z_km - 33.0)*3.3571);
	else if (z_km < 53.0)
		return 265.0;
	else if (z_km < 80.0)
		return 265.0 - ((z_km - 53.0)*2.0370);
	return 210.0;
}

// ITU-R P.835-7, Annex 2, Section 1.2.2.
//
// Returns the total (barometric) pressure (hPa) from geometric height (km) for winter at mid
// latitude (45 deg N).
double ITURP_835_7::WinterMidLatPressure(double z_km)
{
	if (z_km <= 10.0)
		return 1018.8627 - (124.2954*z_km) + (4.8307*z_km*z_km);
	else if (z_km <= 72.0)
		return WinterMidLatPressure(10.0)*std::exp(-0.147*(z_km - 10.0));
	return WinterMidLatPressure(72.0)*std::exp(-0.155*(z_km - 72.0));
}

// ITU-R P.835-7, Annex 2, Section 1.2.2.
//
// Returns the water vapour density (g/m3) from geometric height (km) for winter at mid latitude
// (45 deg N).
double ITURP_835_7::WinterMidLatWaterVapourDensity(double z_km)
{
	if (z_km <= 10.0)
		return 3.4742*std::exp(-(0.2697*z_km) - (0.03604*z_km*z_km) + (0.0004489*z_km*z_km*z_km));
	return 0.0;
}

// ITU-R P.835-7, Annex 2, Section 1.3.1.
//
// Returns the temperature (K) from geometric height (km) for summer at high latitude (60 deg N).
double ITURP_835_7::SummerHighLatTemperature(double z_km)
{
	if (z_km < 10.0)
		return 286.8374 - (4.7805*z_km) - (0.1402*z_km*z_km);
	else if (z_km < 23.0)
		return 225.0;
	else if (z_km < 48.0)
		return 225.0*std::exp((z_km - 23.0)*0.008317);
	else if (z_km < 53.0)
		return 277.0;
	else if (z_km < 79.0)
		return 277.0 - ((z_km - 53.0)*4.0769);
	return 171.0;
}

// ITU-R P.835-7, Annex 2, Section 1.3.1.
//
// Returns the total (barometric) pressure (hPa) from geometric height (km) for summer at high
// latitude (60 deg N).
double ITURP_835_7::SummerHighLatPressure(double z_km)
{
	if (z_km <= 10.0)
		return 1008.0278 - (113.2494*z_km) + (3.9408*z_km*z_km);
	else if (z_km <= 72.0)
		return SummerHighLatPressure(10.0)*std::exp(-0.140*(z_km - 10.0));
	return SummerHighLatPressure(72.0)*std::exp(-0.165*(z_km - 72.0));
}

// ITU-R P.835-7, Annex 2, Section 1.3.1.
//
// Returns the water vapour density (g/m3) from geometric height (km) for summer at high latitude
// (60 deg N).
double ITURP_835_7::SummerHighLatWaterVapourDensity(double z_km)
{
	if (z_km <= 15.0)
		return 8.988*std::exp(-(0.3614*z_km) - (0.005402*z_km*z_km) - (0.001955*z_km*z_km*z_km));
	return 0.0;
}

// ITU-R P.835-7, Annex 2, Section 1.3.2.
//
// Returns the temperature (K) from geometric height (km) for winter at high latitude (60 deg N).
double ITURP_835_7::WinterHighLatTemperature(double z_km)
{
	if (z_km < 8.5)
		return 257.4345 + (2.3474*z_km) - (1.5479*z_km*z_km) + (0.08473*z_km*z_km*z_km);
	else if (z_km < 30.0)
		return 217.5;
	else if (z_km < 50.0)
		return 217.5 + ((z_km - 30.0)*2.125);
	else if (z_km < 54.0)
		return 260.0;
	return 260.0 - ((z_km - 54.0)*1.667);
}

// ITU-R P.835-7, Annex 2, Section 1.3.2.
//
// Returns the total (barometric) pressure (hPa) from geometric height (km) for winter at high
// latitude (60 deg N).
double ITURP_835_7::WinterHighLatPressure(double z_km)
{
	if (z_km <= 10.0)
		return 1010.8828 - (122.2411*z_km) + (4.554*z_km*z_km);
	else if (z_km <= 72.0)
		return WinterHighLatPressure(10.0)*std::exp(-0.147*(z_km - 10.0));
	return WinterHighLatPressure(72.0)*std::exp(-0.150*(z_km - 72.0));
}

// ITU-R P.835-7, Annex 2, Section 1.3.2.
//
// Returns the water vapour density (g/m3) from geometric height (km) for winter at high latitude
// (60 deg N).
double ITURP_835_7::WinterHighLatWaterVapourDensity(double z_km)
{
	if (z_km <= 10.0)
		return 1.2319*std::exp((0.07481*z_km) - (0.0981*z_km*z_km) + (0.00281*z_km*z_km*z_km));
	return 0.0;
}

// ITU-R P.835-7, Annex 2, Section 1.
double ITURP_835_7::SeasonalInterpolate(double z_km, ReferenceAtmosphere seasonal_atm, double lat,
                                        double (*lowLatFunc)(double), double (*summerMidLatFunc)(double),
                                        double (*winterMidLatFunc)(double), double (*summerHighLatFunc)(double),
                                        double (*winterHighLatFunc)(double))
{
	double abs_lat = std::abs(lat);
	if (abs_lat <= 15.0)
		return lowLatFunc(z_km);
	else if (abs_lat >= 60.0)
	{
		if (seasonal_atm == SEASONAL_SUMMER)
			return summerHighLatFunc(z_km);
		return winterHighLatFunc(z_km);
	}

	double x0, x1, y0, y1;
	if (abs_lat < 45.0)
	{
		x0 = 15.0;
		x1 = 45.0;
		y0 = lowLatFunc(z_km);
		if (seasonal_atm == SEASONAL_SUMMER)
			y1 = summerMidLatFunc(z_km);
		else
			y1 = winterMidLatFunc(z_km);
	}
	else
	{
		x0 = 45.0;
		x1 = 60.0;
		if (seasonal_atm == SEASONAL_SUMMER)
		{
			y0 = summerMidLatFunc(z_km);
			y1 = summerHighLatFunc(z_km);
		}
		else
		{
			y0 = winterMidLatFunc(z_km);
			y1 = winterHighLatFunc(z_km);
		}
	}
	double x = abs_lat;
	double y = (y0*(x1 - x) + y1*(x - x0))/(x1 - x0);
	return y;
}
