/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_837_8.h"
#include <stdexcept>
#include <cmath>
#include <cstddef>
#include "ITURP_1510_1.h"


const DigitalMap ITURP_837_8::s_R001_map("p837_8/R001.TXT", -90.0, +0.125, 1441, -180.0, +0.125, 2881, InterpolationType::Bilinear);

const std::vector<DigitalMap> ITURP_837_8::s_MT_Month_maps = []()
{
	std::vector<DigitalMap> maps;
	maps.reserve(12);

	for (int month = 1; month <= 12; ++month)
	{
		char filename[64];
		std::snprintf(filename, sizeof(filename), "p837_8/MT_Month%02d.TXT", month);
		maps.push_back(DigitalMap(filename, -90.125, +0.25, 722, -180.125, +0.25, 1442, InterpolationType::Bilinear));
	}

	return maps;
}(); // () to execute the lambda immediately

double ITURP_837_8::AnnualRainfallRate001(double lat, double lon)
{
	return s_R001_map.GetValue(lat, lon);
}

double ITURP_837_8::TotalMonthlyMeanRainfall(double lat, double lon, int month)
{
	if (month < 1 || month > 12)
		throw std::invalid_argument("Month must be between 1 and 12.");

	std::size_t index = static_cast<std::size_t>(month-1);
	return s_MT_Month_maps[index].GetValue(lat, lon);
}

double ITURP_837_8::Q(double x)
{
    // 1.0 / sqrt(2.0) pre-calculated to maximum double precision
    constexpr double inv_sqrt2 = 0.70710678118654752440; 
    return 0.5 * std::erfc(x * inv_sqrt2);
}

std::pair<double, double> ITURP_837_8::AnnualRainfallRate(double p_percent, double lat, double lon)
{
	// Steps 2 to 7 incl.
	std::array<double, 12> ln_r_list{};
	std::array<double, 12> P0_list{};
	double P0_annual = 0.0;

	for (int month = 1; month <= 12; ++month)
	{
		const double Tii_K = ITURP_1510_1::MonthlyMeanSurfaceTemperature(lat, lon, month);
		const double tii = Tii_K - 273.15;
		const double MTii = TotalMonthlyMeanRainfall(lat, lon, month);

		double rii = 0.5874;
		if (tii >= 0.0)
			rii = 0.5874 * std::exp(0.0883 * tii);

		const std::size_t idx = static_cast<std::size_t>(month - 1);
		const double Nii = s_DaysPerMonth[idx];
		double P0ii = 100.0 * MTii / (24.0 * Nii * rii);
		if (P0ii > 70.0)
		{
			P0ii = 70.0;
			rii = (100.0 / 70.0) * (MTii / (24.0 * Nii));
		}

		ln_r_list[idx] = std::log(rii);
		P0_list[idx] = P0ii;
		P0_annual += Nii * P0ii;
	}
	P0_annual /= 365.25;

	// Step 8
	const double p = p_percent;
	if (p > P0_annual)
	{
		const double Rp = 0.0;
		return {Rp, P0_annual};
	}

	double Rref_a = 0.0;
	double Rref_b = 10000.0;
	double Rref = 0.0;

	while (true)
	{
		Rref = (Rref_a + Rref_b) / 2.0;
		const double ln_Rref = std::log(Rref);
		double P = 0.0;

		for (std::size_t ii = 0; ii < 12; ++ii)
		{
			const double Pii = P0_list[ii] * Q((ln_Rref + 0.7938 - ln_r_list[ii]) / 1.26);
			P += s_DaysPerMonth[ii] * Pii;
		}
		P /= 365.25;

		const double rel_error = 100.0 * std::abs((P / p) - 1.0);
		if (rel_error < 0.001)
			break;

		if (P > p)
			Rref_a = Rref;
		else
			Rref_b = Rref;
	}

	const double Rp = Rref;
	return {Rp, P0_annual};
}

double ITURP_837_8::AnnualProbabilityOfRain(double lat, double lon)
{
	// Steps 2 to 7 incl.
	std::array<double, 12> P0_list{};
	double P0_annual = 0.0;

	for (int month = 1; month <= 12; ++month)
	{
		const double Tii_K = ITURP_1510_1::MonthlyMeanSurfaceTemperature(lat, lon, month);
		const double tii = Tii_K - 273.15;
		const double MTii = TotalMonthlyMeanRainfall(lat, lon, month);

		double rii = 0.5874;
		if (tii >= 0.0)
			rii = 0.5874 * std::exp(0.0883 * tii);

		const std::size_t idx = static_cast<std::size_t>(month - 1);
		const double Nii = s_DaysPerMonth[idx];
		double P0ii = 100.0 * MTii / (24.0 * Nii * rii);
		if (P0ii > 70.0)
			P0ii = 70.0;

		P0_list[idx] = P0ii;
		P0_annual += Nii * P0ii;
	}
	P0_annual /= 365.25;

	return P0_annual;
}

std::pair<double, double> ITURP_837_8::MonthlyRainfallRate(double p_percent, double lat, double lon, int month)
{
	if (month < 1 || month > 12)
		throw std::invalid_argument("month must be between 1 and 12 inclusively.");

	// Steps 2 to 7 incl.
	const double Tii_K = ITURP_1510_1::MonthlyMeanSurfaceTemperature(lat, lon, month);
	const double tii = Tii_K - 273.15;
	const double MTii = TotalMonthlyMeanRainfall(lat, lon, month);

	double rii = 0.5874;
	if (tii >= 0.0)
		rii = 0.5874 * std::exp(0.0883 * tii);

	const std::size_t idx = static_cast<std::size_t>(month - 1);
	const double Nii = s_DaysPerMonth[idx];
	double P0ii = 100.0 * MTii / (24.0 * Nii * rii);
	if (P0ii > 70.0)
	{
		P0ii = 70.0;
		rii = (100.0 / 70.0) * (MTii / (24.0 * Nii));
	}

	// Step 8
	const double p = p_percent;
	if (p > P0ii)
	{
		const double Rp_ii = 0.0;
		return {Rp_ii, P0ii};
	}

	const double ln_rii = std::log(rii);
	double Rref_a = 0.0;
	double Rref_b = 10000.0;
	double Rref = 0.0;

	while (true)
	{
		Rref = (Rref_a + Rref_b) / 2.0;
		const double Pii = P0ii * Q((std::log(Rref) + 0.7938 - ln_rii) / 1.26);

		const double rel_error = 100.0 * std::abs((Pii / p) - 1.0);
		if (rel_error < 0.001)
			break;

		if (Pii > p)
			Rref_a = Rref;
		else
			Rref_b = Rref;
	}

	const double Rp = Rref;
	return {Rp, P0ii};
}

double ITURP_837_8::MonthlyProbabilityOfRain(double lat, double lon, int month)
{
	if (month < 1 || month > 12)
		throw std::invalid_argument("month must be between 1 and 12 inclusively.");

	// Steps 2 to 7 incl.
	const double Tii_K = ITURP_1510_1::MonthlyMeanSurfaceTemperature(lat, lon, month);
	const double tii = Tii_K - 273.15;
	const double MTii = TotalMonthlyMeanRainfall(lat, lon, month);

	double rii = 0.5874;
	if (tii >= 0.0)
		rii = 0.5874 * std::exp(0.0883 * tii);

	const std::size_t idx = static_cast<std::size_t>(month - 1);
	const double Nii = s_DaysPerMonth[idx];
	double P0ii = 100.0 * MTii / (24.0 * Nii * rii);
	if (P0ii > 70.0)
	{
		P0ii = 70.0;
		rii = (100.0 / 70.0) * (MTii / (24.0 * Nii));
	}

	return P0ii;
}
