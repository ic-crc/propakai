/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_840_9.h"
#include <stdexcept>
#include <cstddef>
#include <cmath>
#include "ITURP_1057_7.h"


const std::vector<ITURP_840_9::PFile> ITURP_840_9::s_ANNUAL_P_FILES = {
	{0.01, "L_001"}, {0.02, "L_002"}, {0.03, "L_003"}, {0.05, "L_005"},
	{0.1,  "L_01"},  {0.2,  "L_02"},  {0.3,  "L_03"},  {0.5,  "L_05"},
	{1.0,  "L_1"},   {2.0,  "L_2"},   {3.0,  "L_3"},   {5.0,  "L_5"},
	{10.0, "L_10"},  {20.0, "L_20"},  {30.0, "L_30"},  {50.0, "L_50"},
	{60.0, "L_60"},  {70.0, "L_70"},  {80.0, "L_80"},  {90.0, "L_90"},
	{95.0, "L_95"},  {99.0, "L_99"},  {100.0, "L_100"}
};

const std::vector<ITURP_840_9::PFile> ITURP_840_9::s_MONTHLY_P_FILES = {
	{0.1,  "L_01"},  {0.2,  "L_02"},  {0.3,  "L_03"},  {0.5,  "L_05"},
	{1.0,  "L_1"},   {2.0,  "L_2"},   {3.0,  "L_3"},   {5.0,  "L_5"},
	{10.0, "L_10"},  {20.0, "L_20"},  {30.0, "L_30"},  {50.0, "L_50"},
	{60.0, "L_60"},  {70.0, "L_70"},  {80.0, "L_80"},  {90.0, "L_90"},
	{95.0, "L_95"},  {99.0, "L_99"},  {100.0, "L_100"}
};

const std::array<std::string, 12> ITURP_840_9::s_MONTH_FOLDERS = {
	"01/", "02/", "03/", "04/", "05/", "06/", "07/", "08/", "09/", "10/", "11/", "12/"
};

DigitalMap make_p840_9_map(const std::string& filename)
{
    return { filename, -90.0, +0.25, 721, -180.0, +0.25, 1441, InterpolationType::Bilinear };
}

const std::unordered_map<std::string, DigitalMap> ITURP_840_9::s_Annual_maps = []()
{
	std::unordered_map<std::string, DigitalMap> annual_maps;

    for (const PFile& pfile : s_ANNUAL_P_FILES)
	{
        std::string path = "p840_9/annual/" + pfile.filenameNoExt + ".TXT";
        annual_maps.emplace(pfile.filenameNoExt, make_p840_9_map(path));
    }

	annual_maps.emplace("L_mean", make_p840_9_map("p840_9/annual/L_mean.TXT"));
	annual_maps.emplace("L_std", make_p840_9_map("p840_9/annual/L_std.TXT"));
	annual_maps.emplace("mL", make_p840_9_map("p840_9/annual/mL.TXT"));
	annual_maps.emplace("PL", make_p840_9_map("p840_9/annual/PL.TXT"));
	annual_maps.emplace("sL", make_p840_9_map("p840_9/annual/sL.TXT"));

	return annual_maps;
}();

const std::unordered_map<std::string, DigitalMap> ITURP_840_9::s_Monthly_maps = []()
{
	std::unordered_map<std::string, DigitalMap> monthly_maps;

	for (std::string_view month : s_MONTH_FOLDERS) 
	{
		for (const PFile& pfile : s_MONTHLY_P_FILES)
		{
			std::string key = std::string(month) + pfile.filenameNoExt;
			std::string path = "p840_9/monthly/" + key + ".TXT";
			monthly_maps.emplace(key, make_p840_9_map(path));
		}

		std::string mean_key = std::string(month) + "L_mean";
		monthly_maps.emplace(mean_key, make_p840_9_map("p840_9/monthly/" + mean_key + ".TXT"));

		std::string std_key = std::string(month) + "L_std";
		monthly_maps.emplace(std_key, make_p840_9_map("p840_9/monthly/" + std_key + ".TXT"));
	}

	return monthly_maps;
}();

const DigitalMap& ITURP_840_9::GetDigitalMap(int month, const std::string& filenameNoExt)
{
	if (month == -1)
		return s_Annual_maps.at(filenameNoExt);

	if (month >= 1 && month <= 12)
	{
		std::size_t index = static_cast<std::size_t>(month-1);
		return s_Monthly_maps.at(s_MONTH_FOLDERS[index] + filenameNoExt);
	}

	throw std::invalid_argument("Month must be between 1 and 12, or -1 for annual data.");
}

static constexpr double radians(double deg)
{
	return deg * (3.14159265358979323846 / 180.0);
}

double ITURP_840_9::CloudOrFogAttenuation(double f_GHz, double T_K, double rhol_gm3)
{
	const double gamma_c = CloudLiquidWaterAttenuationCoefficient(f_GHz, T_K)*rhol_gm3;
	return gamma_c;
}

double ITURP_840_9::CloudLiquidWaterAttenuationCoefficient(double f_GHz, double T_K)
{
	const double a = (300.0/T_K)-1.0;
	const double fp = 20.20 - 146.0*a + 316.0*a*a;
	const double fs = 39.8*fp;
	const double eps0 = 77.66 + 103.3*a;
	const double eps1 = 0.0671*eps0;
	constexpr double eps2 = 3.52;
	const double xp = 1.0 + (f_GHz*f_GHz)/(fp*fp);
	const double xs = 1.0 + (f_GHz*f_GHz)/(fs*fs);
	const double eps_pp = f_GHz*(eps0-eps1)/(fp*xp) + f_GHz*(eps1-eps2)/(fs*xs);
	const double eps_p = (eps0-eps1)/xp + (eps1-eps2)/xs + eps2;
	const double n = (2+eps_p)/eps_pp;
	const double Kl = 0.819*f_GHz/(eps_pp*(1.0+(n*n)));
	return Kl;
}

double ITURP_840_9::SlantPathInstantaneousCloudAttenuation(double f_GHz, double theta_deg, double L_kgm2)
{
	const double Ac = KL(f_GHz)*L_kgm2/std::sin(radians(theta_deg));
	return Ac;
}

double ITURP_840_9::SlantPathStatisticalCloudAttenuation(double f_GHz, double theta_deg, double p_percent,
                                                         double lat, double lon, int month)
{
	const double L = IntegratedCloudLiquidWaterContent(p_percent, lat, lon, month);
	const double Ac = SlantPathInstantaneousCloudAttenuation(f_GHz, theta_deg, L);
	return Ac;
}

double ITURP_840_9::LogNormalApproxToStatCloudAttenuation(double f_GHz, double theta_deg, double p_percent,
                                                          double lat, double lon)
{
	const double PL = GetDigitalMap(-1, "PL").GetValue(lat, lon);
	if (PL <= 0.02)
		return 0.0;
	if (p_percent >= PL)
		return 0.0;
	const double mL = GetDigitalMap(-1, "mL").GetValue(lat, lon);
	const double sL = GetDigitalMap(-1, "sL").GetValue(lat, lon);
	const double K_L = KL(f_GHz);
	const double Ac = K_L*std::exp(mL+(sL*ITURP_1057_7::Qinv(p_percent/PL)))/std::sin(radians(theta_deg));
	return Ac;
}

double ITURP_840_9::IntegratedCloudLiquidWaterContent(double p_percent, double lat, double lon, int month)
{
	const std::vector<PFile>& pFiles = (month == -1) ? s_ANNUAL_P_FILES : s_MONTHLY_P_FILES;

	for (size_t i=0; i<pFiles.size()-1; ++i)
	{
		if (p_percent == pFiles[i].p)
			return GetDigitalMap(month, pFiles[i].filenameNoExt).GetValue(lat, lon); // no need for interpolation

		if (p_percent > pFiles[i].p && p_percent < pFiles[i+1].p)
		{
			const double L0 = GetDigitalMap(month, pFiles[i].filenameNoExt).GetValue(lat, lon);
			const double L1 = GetDigitalMap(month, pFiles[i+1].filenameNoExt).GetValue(lat, lon);
			const double p0 = pFiles[i].p; // p below
			const double p1 = pFiles[i+1].p; // p above
			const double L = (L0*std::log10(p1/p_percent) + L1*std::log10(p_percent/p0)) / std::log10(p1/p0);
			return L;
		}
	}

	// check for exact match on the last percentage
	if (p_percent == pFiles.back().p)
		return GetDigitalMap(month, pFiles.back().filenameNoExt).GetValue(lat, lon);

	throw std::invalid_argument("p_percent is out of range.");
}

double ITURP_840_9::MeanIntegratedCloudLiquidWaterContent(double lat, double lon, int month)
{
	return GetDigitalMap(month, "L_mean").GetValue(lat, lon);
}

double ITURP_840_9::StdDevIntegratedCloudLiquidWaterContent(double lat, double lon, int month)
{
	return GetDigitalMap(month, "L_std").GetValue(lat, lon);
}

// ITU-R P.840-9, Annex 1, Section 3.1.
// 
// Gets the cloud liquid mass absorption coefficient in dB/(kg/m2) or dB/mm.
// 
// f_ghz: Frequency (GHz).
// Returns: The cloud liquid mass absorption coefficient, KL, in dB/(kg/m2) or dB/mm.
double ITURP_840_9::KL(double f_GHz)
{
	constexpr double A1 = 0.1522;
	constexpr double A2 = 11.51;
	constexpr double A3 = -10.4912;
	constexpr double f1 = -23.9589;
	constexpr double f2 = 219.2096;
	constexpr double s1 = 3.2991E3;
	constexpr double s2 = 2.7595E6;
	const double e1 = std::exp(-((f_GHz-f1)*(f_GHz-f1))/s1);
	const double e2 = std::exp(-((f_GHz-f2)*(f_GHz-f2))/s2);
	const double KL = CloudLiquidWaterAttenuationCoefficient(f_GHz, 273.75)* ((A1*e1) + (A2*e2) + A3);
	return KL;
}
